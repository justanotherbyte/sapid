from __future__ import annotations

import inspect
import logging
from typing import (
    TYPE_CHECKING,
    Dict,
    Union,
    Optional
)

from .repository import Repository
from .installation import Installation
from .issue import Issue
from .comment import Comment
from .user import BaseUser

if TYPE_CHECKING:
    from .bot import GitBot
    from .user import (
        BaseUser,
        User,
        ApplicationUser
    )


__all__ = (
    "ApplicationState",
)

_log = logging.getLogger(__name__)

class ApplicationState:
    """
    This class does not remove the library from stateless project options.
    This class is simply a class that holds internal caches and parses 
    events properly.
    """
    def __init__(self, bot: GitBot):
        self._bot = bot
        self._http = bot.http
        self._user: Optional[ApplicationUser] = None
        self._dispatch = bot.dispatch # just a shortcut for convenience

        # caches
        self._users: Dict[int, Union[BaseUser, User]] = {}
        self._installations: Dict[int, Installation] = {}
        self._issues: Dict[int, Issue] = {}

        self.parsers = parsers = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                parsers[attr] = func

    async def _call_initial_endpoints(self):
        # calls the relevant endpoints to fill the caches.
        raw_installations = await self._http.fetch_installations()
        # raw_issues = await self._http.fetch_all_issues()
        raw_issues = [] # the http call currently is broken.
        
        for installation in raw_installations:
            installation_id = installation["id"]
            self._installations[installation_id] = Installation(state=self, data=installation)
        
        for issue in raw_issues:
            repo_data = issue["repository"]
            repo = Repository(state=self, data=repo_data)
            _issue = Issue(state=self, data=issue, repository=repo)
            issue_id = issue["id"]
            self._issues[issue_id] = _issue

        
    def get_user(self, id: int, /) -> Optional[Union[BaseUser, User]]:
        user = self._users.get(id)
        return user

    def get_installation(self, id: int, /) -> Optional[Installation]:
        installation = self._installations.get(id)
        return installation
    
    def parse_star(self, data):
        repository = data["repository"]
        action = data["action"]

        repository = Repository(state=self, data=repository)
        self._dispatch("repository_star_update", action, repository)

    def parse_issue_comment(self, data):
        # ['action', 'changes', 'issue', 'comment', 'repository', 'sender', 'installation']
        event = "comment_"
        action = data["action"]
        _issue = data["issue"]
        _comment = data["comment"]
        _repository = data["repository"]
        _sender = data["sender"]

        repo = Repository(state=self, data=_repository)
        issue = Issue(state=self, data=_issue, repository=repo)
        comment = Comment(state=self, data=_comment, issue=issue)
        sender = BaseUser(state=self, data=_sender)

        if action == "edited": 
            # if a comment was edited
            # we want to parse out the changes key
            # and dispatch a different event
            event += "edit"
            changes = data["changes"] # this key only exists when a comment is edited
            return self._dispatch(
                event,
                changes,
                comment,
                issue,
                repo,
                sender
            )

        if action == "created":
            # when a comment is created
            event += "create"
            return self._dispatch(
                event,
                comment,
                issue,
                repo,
                sender
            )

        _log.debug(f"Received a {action} comment event that has not been handled.")