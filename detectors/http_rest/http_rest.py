import json

from aiohttp import web, web_request

from task_executer.lib.detector import Detector


class HttpRestDetector(Detector):

    def __init__(self):
        super().__init__("http_rest")

    def init(self):
        self.port = self.config.get_int("port", 8080)
        self.host = self.config.get_string("host", "0.0.0.0")
        self.app = web.Application()
        self.app.router.add_get(self.config.get_string("path", "/"), handler=self.on_package_received)
        self.app.router.add_post(self.config.get_string("path", "/"), handler=self.on_package_received)
        self.site = None

    async def start(self) -> bool:
        runner = web.AppRunner(self.app)
        await runner.setup()
        self.site = web.TCPSite(runner, self.host, self.port)

        await self.site.start()
        self.logger.info(f"Started Webserver @ {self.host}:{self.port}")
        return True

    async def on_package_received(self, request: web_request.Request) -> web.Response:
        if request.method == "GET":
            data = dict(request.query)
        elif request.method == "POST":
            if not request.body_exists:
                return web.Response(status=400, text="No Data Provided")

            raw_data = ""
            try:
                raw_data = await request.content.readline()
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                self.logger.warn(f"Could not read Json POST Data {raw_data}", exc_info=True)
                return web.Response(status=400, text="Invalid Json Request")
            except Exception:
                self.logger.warn("Could not read POST Data", exc_info=True)
                return web.Response(status=400, text="Invalid Request")

        else:
            return web.Response(status=403, text="Invalid Method")

        all_parameter_present = True
        for i in ("task", "token"):
            if i not in data:
                all_parameter_present = False

        if all_parameter_present:
            if self.detector_callback.on_task_detected(
                    task_name=data["task"],
                    task_token=data["token"],
                    optional_parameters=data
            ):
                return web.Response(status=200, text="OK")
            else:
                return web.Response(status=500, text="Error")
        else:
            self.logger.warning(
                f"Cannot start task from http webserver because parameters were missing, provided data: {data}")
            return web.Response(status=403, text="Invalid Parameters")

    async def stop(self):
        if self.site is not None:
            await self.site.stop()
