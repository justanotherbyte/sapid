from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Union
)

from .user import BaseUser
from .comment import Comment
from .enums import IssueLockReason
from .utils import Cacheable, _parse_list_to_object

if TYPE_CHECKING:
    from .state import ApplicationState
    from .repository import Repository
    from .types.issue import Issue as IssuePayload


class Issue(Cacheable):

    if TYPE_CHECKING:
        url: str
        repository_url: str
        labels_url: str
        comments_url: str
        events_url: str
        html_url: str
        id: int
        node_id: str
        number: int
        title: str
        user: Dict[str, Union[bool, str, int]]
        labels: List[str]
        state: str
        locked: bool
        assignee: Optional[BaseUser]
        assignees: List[BaseUser]
        comments: int
        created_at: str
        updated_at: str
        closed_at: str
        author_association: str
        body: str
        reactions: Dict[str, Union[str, int]]
        timeline_url: str
        performed_via_github_app: Optional[bool]
        repository: Repository

    def __init__(self, *, state: ApplicationState, data: IssuePayload, repository: Repository):
        self._state = state
        self._update(data, repository)

    async def lock(self, *, reason: Optional[IssueLockReason] = None):
        access_token = await self.repository.fetch_access_token(cache=True)
        await self._state._http.lock_issue(
            owner=self.repository.owner.login,
            repo=self.repository.name,
            issue_number=self.number,
            access_token=access_token["token"],
            reason=reason
        )

    async def create_comment(self, body: str) -> Comment:
        access_token = await self.repository.fetch_access_token(cache=True)
        data = await self._state._http.create_issue_comment(
            owner=self.repository.owner.login,
            repo=self.repository.name,
            issue_number=self.number,
            body=body,
            access_token=access_token["token"]
        )
        comment = Comment(state=self._state, data=data, issue=self)
        return comment
    
    def _update(self, data: IssuePayload, repository: Repository):
        self.url = data["url"]        
        self.repository_url = data["repository_url"]
        self.labels_url = data["labels_url"]
        self.comments_url = data["comments_url"]
        self.events_url = data["events_url"]
        self.html_url = data["html_url"]
        self.id = data["id"]
        self.node_id = data["node_id"]
        self.number = data["number"]
        self.title = data["title"]
        self.user = data["user"]
        self.labels = data["labels"]
        self.state = data["state"]
        self.locked = data["locked"]
        self.assignee = data["assignee"]
        self.assignees = data["assignees"]
        self.comments = data["comments"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.closed_at = data["closed_at"]
        self.author_association = data["author_association"]
        self.body = data["body"]
        self.reactions = data["reactions"]
        self.timeline_url = data["timeline_url"]
        self.performed_via_github_app = data["performed_via_github_app"]
        self.repository = repository

        if self.assignee is not None:
            _user = BaseUser(state=self._state, data=self.assignee)
            self.assignee = _user
        
        self.assignees = _parse_list_to_object(BaseUser, state=self._state, data=self.assignees)