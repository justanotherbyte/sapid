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


class ApplicationState:
    def __init__(self, bot: GitBot):
        self._bot = bot
        self._http = bot.http
        self._user: Optional[ApplicationUser] = None
        self._dispatch = bot.dispatch # just a shortcut for convenience

        # caches
        self._users: Dict[int, Union[BaseUser, User]] = {}

        self.parsers = parsers = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                parsers[attr] = func

    def get_user(self, id: int, /) -> Optional[Union[BaseUser, User]]:
        user = self._users.get(id)
        return user
    
    def parse_star(self, data):
        repository = data["repository"]
        action = data["action"]

        repository = Repository(state=self, data=repository)
        self._dispatch("repository_star", action, repository)