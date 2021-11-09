from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Dict,
    Union,
    Optional
)

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

        # caches
        self._users: Dict[int, Union[BaseUser, User]] = {}

    def get_user(self, id: int, /) -> Optional[Union[BaseUser, User]]:
        user = self._users.get(id)
        return user

    


    