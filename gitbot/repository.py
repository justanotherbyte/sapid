from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Optional,
    Dict,
    List,
    Any
)

from .user import BaseUser
from .utils import parse_to_dt

if TYPE_CHECKING:
    from .state import ApplicationState
    from .types.repository import Respository as RepositoryPayload


class Repository:

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
