import asyncio
import logging
import signal
from typing import (
    Optional,
    Dict,
    Awaitable,
    List,
    Union
)

import aiohttp

from .http import HTTPClient, AuthInfo
from .server import WebhookServer
from .state import ApplicationState
from .user import ApplicationUser, BaseUser, User


_log = logging.getLogger(__name__)

class GitBot:
    def __init__(
        self,
        pem_file_fp: str,
        app_id: str,
        webhook_secret: str,
        client_secret: str,
        client_id: str,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        session: Optional[aiohttp.ClientSession] = None,
        endpoint: Optional[str] = None,
        apply_proxy_support: bool = False
    ):
        auth = AuthInfo(
            pem_fp=pem_file_fp,
            app_id=app_id,
            client_secret=client_secret,
            client_id=client_id
        )
        
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self.http = HTTPClient(auth, loop=self.loop, session=session)

        _endpoint = endpoint or "/gitbot-interaction-receive"
        __state = ApplicationState(self)
        self.server = WebhookServer(
            webhook_secret=webhook_secret,
            endpoint=_endpoint,
            state=__state,
            behind_proxy=apply_proxy_support
        )

        self._state = __state
        self.__listeners: Dict[str, List[Awaitable]] = {}

    async def start(
        self,
        *,
        host: str = "0.0.0.0",
        port: int = 8000
    ):
        server = self.server
        
        self.http.recreate()  # Initial session creation
        _app_info = await self.http.fetch_app()
        _app_user = ApplicationUser(state=self._state, data=_app_info)
        _log.info(f"Identified Application: owner: {_app_user.owner.login}: name: {_app_user.name}: app_id: {_app_user.id}")
        self._state._user = _app_user

        await self._state._call_initial_endpoints()

        await server._run(host=host, port=port, dispatch=self.dispatch)
        _log.info(f"TCP server is now online at: http://{host}:{port}")

    def run(
        self,
        *,
        host: str = "0.0.0.0",
        port: int = 8000
    ):
        loop = self.loop

        try:
            loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
            loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
        except NotImplementedError:
            pass
        
        loop.run_until_complete(self.start(host=host, port=port))
        loop.run_forever()

    async def close(self):
        await self.server.cleanup()
        await self.http.close()
        

    def dispatch(self, event_name: str, *args):
        event_name = "on_" + event_name
        listeners = self.__listeners.get(event_name, [])

        for i, callback in enumerate(listeners):
            self.loop.create_task(callback(*args), name=f"gitbot:{event_name}:{i}")

    def add_listener(self, event_name: str, callback: Awaitable):
        if not asyncio.iscoroutinefunction(callback):
            raise ValueError("Listener callback must be a coroutine.")

        event_name = event_name.lower()

        current_listeners = self.__listeners.get(event_name, [])
        current_listeners.append(callback)

        self.__listeners[event_name] = current_listeners

    def event(self, coro: Awaitable):
        self.add_listener(coro.__name__, coro)

    @property
    def user(self) -> ApplicationUser:
        return self._state._user

    def get_user(self, id: int, /) -> Optional[Union[BaseUser, User]]:
        user = self._state.get_user(id)
        return user


        
