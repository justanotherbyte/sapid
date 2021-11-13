from __future__ import annotations

from typing import (
    TYPE_CHECKING
)

from .user import BaseUser
from .utils import Cacheable, parse_to_dt

if TYPE_CHECKING:
    from .issue import Issue
    from .state import ApplicationState
    from .types.issue import Issue as IssuePayload


class Comment(Cacheable):
    
    if TYPE_CHECKING:
        id: int
        node_id: str
        url: str
        html_url: str
        body: str
        user: BaseUser
        created_at: str
        updated_at: str
        issue_url: str
        author_association: str

    def __init__(self, *, state: ApplicationState, data: IssuePayload, issue: Issue):
        self._state = state
        self._update(data, issue)
    
    def _update(self, data: IssuePayload, issue: IssuePayload):
        self.id = data["id"]
        self.node_id = data["node_id"]
        self.url = data["url"]
        self.html_url = data["html_url"]
        self.body = data["body"]
        self.user = BaseUser(state=self._state, data=data["user"])
        self.created_at = parse_to_dt(data["created_at"])
        self.updated_at = parse_to_dt(data["updated_at"])
        self.issue_url = data["issue_url"]
        self.author_association = data["author_association"]
        self.issue = issue

