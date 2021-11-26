from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Optional,
    Dict,
    List,
    Any
)

from .user import BaseUser
from .issue import Issue
from .enums import IssueLockReason
from .installation import Installation
from .utils import parse_to_dt, Cacheable, NUMSTR

if TYPE_CHECKING:
    from .state import ApplicationState
    from .types.repository import Respository as RepositoryPayload


__all__ = (
    "Repository",
)

class Repository(Cacheable):

    if TYPE_CHECKING:
        id: int
        node_id: str
        name: str
        full_name: str
        private: bool
        owner: BaseUser
        html_url: str
        description: str
        fork: bool
        url: str
        created_at: str
        updated_at: str
        pushed_at: str
        git_url: str
        ssh_url: str
        clone_url: str
        svn_url: str
        homepage: Optional[str]
        size: int
        stargazers_count: int
        watchers_count: int
        language: Optional[str]
        has_issues: bool
        has_projects: bool
        has_downloads: bool
        has_wiki: bool
        has_pages: bool
        forks_count: int
        mirror_url: Optional[str]
        archived: bool
        disabled: bool
        open_issues_count: int
        license: Optional[str]
        allow_forking: bool
        is_template: bool
        topics: List[str]
        visibility: str
        forks: int
        open_issues: int
        watchers: int
        default_branch: str

    def __init__(self, *, state: ApplicationState, data: RepositoryPayload):
        self._state = state
        self._update(data)

    def __repr__(self) -> str:
        fmt = "<Repository id={0.id!r} name={0.name!r} owner={0.owner.login!r}>"
        return fmt.format(self)

    async def fetch_contributors(self) -> List[BaseUser]:
        _cs = []
        contributors_raw = await self._state._http.fetch_repository_contributors(self.owner.login, self.name)
        for payload in contributors_raw:
            _user = BaseUser(state=self._state, data=payload)
            _cs.append(_user)

        return _cs

    async def fetch_installation(self, *, cache: bool = False) -> Installation:
        if cache:
            opt_installation = self.get_cache("__installation__")
            if opt_installation:
                return opt_installation
        
        data = await self._state._http.fetch_repo_installation(
            owner=self.owner.login,
            repo=self.name
        )
        installation = Installation(state=self._state, data=data)
        self.set_cache("__installation__", installation) # this does not depend on the cache kwarg. We cache it regardless.
        return installation

    async def fetch_access_token(self, *, cache: bool = False) -> dict:
        if cache:
            opt_ac = self.get_cache("__access_token__")
            if opt_ac:
                return opt_ac
        
        installation = await self.fetch_installation(cache=True)
        data = await self._state._http.fetch_access_token(installation.id)
        self.set_cache("__access_token__", data)
        return data

    async def fetch_issue(self, issue_number: NUMSTR) -> Issue:
        payload = await self._state._http.fetch_issue(
            owner=self.owner.login,
            repo=self.name,
            issue_number=issue_number
        )
        issue = Issue(state=self._state, data=payload, repository=self)
        return issue
    
    async def create_issue(
        self,
        *,
        title: str,
        body: str,
        assignee: Optional[str] = None,
        milestone: Optional[int] = None,
        labels: List[str] = [],
        assignees: List[str] = []
    ) -> Issue:
        access_token = await self.fetch_access_token(cache=True)
        data = await self._state._http.create_issue(
            owner=self.owner.login,
            repo=self.name,
            access_token=access_token["token"],
            title=title,
            body=body,
            assignee=assignee,
            milestone=milestone,
            labels=labels,
            assignees=assignees
        )
        issue = Issue(state=self._state, data=data, repository=self)
        return issue

    @property
    def installation(self) -> Optional[Installation]:
        return self.get_cache("__installation__")
    

    def _update(self, data: RepositoryPayload):
        self.id = data["id"]
        self.node_id = data["node_id"]
        self.name = data["name"]
        self.full_name = data["full_name"]
        self.private = data["private"]
        self.owner = BaseUser(state=self._state, data=data["owner"])
        self.html_url = data["html_url"]
        self.description = data["description"]
        self.fork = data["fork"]
        self.url = data["url"]
        self.created_at = parse_to_dt(data["created_at"])
        self.updated_at = parse_to_dt(data["updated_at"])
        self.pushed_at = data["pushed_at"]
        self.git_url = data["git_url"]
        self.ssh_url = data["ssh_url"]
        self.clone_url = data["clone_url"]
        self.svn_url = data["svn_url"]
        self.homepage = data["homepage"]
        self.size = data["size"]
        self.stargazers_count = data["stargazers_count"]
        self.watchers_count = data["watchers_count"]
        self.language = data["language"]
        self.has_issues = data["has_issues"]
        self.has_projects = data["has_projects"]
        self.has_downloads = data["has_downloads"]
        self.has_wiki = data["has_wiki"]
        self.has_pages = data["has_pages"]
        self.forks_count = data["forks_count"]
        self.mirror_url = data["mirror_url"]
        self.archived = data["archived"]
        self.disabled = data["disabled"]
        self.open_issues_count = data["open_issues_count"]
        self.license = data["license"]
        self.allow_forking = data["allow_forking"]
        self.is_template = data["is_template"]
        self.topics = data["topics"]
        self.visibility = data["visibility"]
        self.forks = data["forks"]
        self.open_issues = data["open_issues"]
        self.watchers = data["watchers"]
        self.default_branch = data["default_branch"]
