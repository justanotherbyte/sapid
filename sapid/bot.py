import asyncio
import logging
import signal
import traceback
import sys
from typing import (
    Any,
    Optional,
    Dict,
    Awaitable,
    List,
    Union,
    Coroutine,
    Callable
)

import aiohttp

from .http import HTTPClient, AuthInfo
from .server import WebhookServer
from .state import ApplicationState
from .user import ApplicationUser, BaseUser, User


__all__ = (
    "GitBot",
)

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
        self._closed = False
        self._done_ev = asyncio.Event()
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

        async def runner():
            try:
                await self._done_ev.wait()
            except KeyboardInterrupt:
                if not self.is_closed():
                    await self.close()

        def stop_on_completion(_):
            loop.stop()        

        future = asyncio.ensure_future(runner(), loop=loop)
        future.add_done_callback(stop_on_completion)

        loop.run_until_complete(self.start(host=host, port=port))
        loop.run_forever()

    async def close(self):
        self._done_ev.set()
        await self.server.cleanup()
        await self.http.close()
        self._closed = True

    def is_closed(self) -> bool:
        return self._closed

    async def _run_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event: str,
        *args: Any,
        **kwargs: Any
    ):
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception:
            await self.on_internal_error(event, *args, **kwargs)

    def _schedule_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event: str,
        idx: int,
        *args: Any,
        **kwargs: Any
    ):
        wrapped = self._run_event(coro, event, *args, **kwargs)
        asyncio.create_task(wrapped, name=f"sapid: {event}: {idx}")
        
    def dispatch(self, event_name: str, *args, **kwargs):
        _log.debug("Dispatching event %s" % event_name)

        listener_name = "on_" + event_name
        listeners = self.__listeners.get(listener_name, [])

        for i, callback in enumerate(listeners):
            self._schedule_event(callback, event_name, i, *args, **kwargs)

    def add_listener(self, event_name: str, callback: Awaitable):
        if not asyncio.iscoroutinefunction(callback):
            raise ValueError("Listener callback must be a coroutine.")

        event_name = event_name.lower()

        current_listeners = self.__listeners.get(event_name, [])
        current_listeners.append(callback)

        self.__listeners[event_name] = current_listeners

    async def on_internal_error(self, event: str, *args: Any, **kwargs: Any) -> None:
        print(f'Ignoring exception in {event}', file=sys.stderr)
        traceback.print_exc()


    def event(self, coro: Awaitable):
        self.add_listener(coro.__name__, coro)

    @property
    def user(self) -> ApplicationUser:
        return self._state._user

    def get_user(self, id: int, /) -> Optional[Union[BaseUser, User]]:
        user = self._state.get_user(id)
        return user


        
