from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Dict,
    Union,
    Optional
)

from .repository import Repository

if TYPE_CHECKING:
    from .bot import GitBot
    from .user import (
        BaseUser,
        User,
        ApplicationUser
    )
    from .utils import PAYLOADITEMTYPE


class ApplicationState:
    def __init__(self, bot: GitBot):
        self._bot = bot
        self._http = bot.http
        self._user: Optional[ApplicationUser] = None
        self._dispatch = bot.dispatch # just a shortcut for convenience

        # caches
        self._users: Dict[int, Union[BaseUser, User]] = {}
        self._installations: Dict[int, Dict[str, PAYLOADITEMTYPE]] = {}

        self.parsers = parsers = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                parsers[attr] = func

    async def _call_initial_endpoints(self):
        # calls the relevant endpoints to fill the caches.
        raw_installations = await self._http.fetch_installations()
        
        for installation in raw_installations:
            installation_id = installation["id"]
            self._installations[installation_id] = installation

    def get_user(self, id: int, /) -> Optional[Union[BaseUser, User]]:
        user = self._users.get(id)
        return user

    def get_installation(self, id: int, /) -> Optional[Dict[str, PAYLOADITEMTYPE]]:
        installation = self._installations.get(id)
        return installation
    
    def parse_star(self, data):
        repository = data["repository"]
        action = data["action"]

        repository = Repository(state=self, data=repository)
        self._dispatch("repository_star_update", action, repository)