from typing import Optional, Callable

from aiohttp import web


class WebhookServer:
    def __init__(
        self,
        webhook_secret: str,
        endpoint: str = "/gitbot-interaction-receive"
    ):
        self._app = web.Application()
        self._tcp: Optional[web.TCPSite] = None
        self._runner: Optional[web.AppRunner] = None

        self.wh_secret = webhook_secret
        self.wh_endpoint = endpoint

    async def handle_interaction(self, request: web.Request):
        headers = request.headers
        print(request)
        # TODO: Handle interactions.

        return web.Response(status=200)

    async def _run(self, host: str, port: int, dispatch: Callable):
        endpoint = self.wh_endpoint
        self._app.router.add_post(endpoint, self.handle_interaction)

        self._runner = web.AppRunner(self._app)
        await self._runner.setup()

        self._tcp = web.TCPSite(self._runner, host=host, port=str(port))
        await self._tcp.start()
        dispatch("gitbot_tcp_ready", host, port)

    async def cleanup(self):
        if self._tcp:
            await self._tcp.stop()
        if self._runner:
            await self._runner.cleanup()