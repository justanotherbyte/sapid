from __future__ import annotations

from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Optional,
    Dict,
    List
)

from .utils import parse_to_dt

if TYPE_CHECKING:
    from .types.user import User as UserPayload
    from .types.user import ApplicationUser as ApplicationUserPayload
    from .state import ApplicationState


__all__ = (
    "BaseUser",
    "User",
)

class BaseUser:

    if TYPE_CHECKING:
        login: str
        id: int
        node_id: str
        avatar_url: str
        url: str
        html_url: str
        followers_url: str
        following_url: str
        gists_url: str
        starred_url: str
        subscriptions_url: str
        organizations_url: str
        repos_url: str
        events_url: str
        received_events_url: str
        type: str
        site_admin: bool

    def __init__(self, *, state: ApplicationState, data: UserPayload):
        self._state = state
        self._update(data)

    def _update(self, data: UserPayload):
        self.login = data["login"]
        self.id = data["id"]
        self.node_id = data["node_id"]
        self.avatar_url = data["avatar_url"]
        self.url = data["url"]
        self.html_url = data["html_url"]
        self.followers_url = data["html_url"]
        self.following_url = data["following_url"]
        self.gists_url = data["gists_url"]
        self.starred_url = data["starred_url"]
        self.subscriptions_url = data["subscriptions_url"]
        self.organizations_url = data["organizations_url"]
        self.repos_url = data["repos_url"]
        self.events_url = data["events_url"]
        self.received_events_url = data["received_events_url"]
        self.type = data["type"]
        self.site_admin = data["site_admin"]

class User(BaseUser):

    if TYPE_CHECKING:
        name: Optional[str]
        company: Optional[str]
        blog: Optional[str]
        location: Optional[str]
        email: Optional[str]
        hireable: Optional[bool]
        bio: Optional[str]
        twitter_username: Optional[str]
        public_repos: Optional[int]
        public_gists: Optional[int]
        followers: Optional[int]
        following: Optional[int]
        created_at: Optional[datetime]
        updated_at: Optional[datetime]
        private_gists: Optional[int]
        total_private_repos: Optional[int]
        owned_private_repos: Optional[int]
        disk_usage: Optional[int]
        collaborators: Optional[int]
        two_factor_authentication: Optional[bool]
        gravatar_id: Optional[str]
        plan: Optional[dict]

    def __init__(self, *, state: ApplicationState, data: UserPayload):
        super().__init__(state=state, data=data)

    def _update(self, data: UserPayload):
        super()._update(data)
        self.name = data.get("name")
        self.company = data.get("company")
        self.blog = data.get("blog")
        self.location = data.get("location")
        self.email = data.get("email")
        self.hireable = data.get("hireable")
        self.bio = data.get("bio")
        self.twitter_username = data.get("twitter_username")
        self.public_repos = data.get("public_repos")
        self.public_gists = data.get("public_gists")
        self.followers = data.get("followers")
        self.following = data.get("following")
        self._created_at = data.get("created_at")
        self._updated_at = data.get("updated_at")
        self.private_gists = data.get("private_gists")
        self.total_private_repos = data.get("total_private_repos") 
        self.owned_private_repos = data.get("owned_private_repos") 
        self.disk_usage = data.get("disk_usage") 
        self.collaborators = data.get("collaborators") 
        self.two_factor_authentication = data.get("two_factor_authentication") 
        self.gravatar_id = data.get("gravatar_id") 
        self.plan = data.get("plan") 

    @property
    def created_at(self) -> datetime:
        _created_at = self._created_at
        dt = parse_to_dt(_created_at)
        return dt

    @property
    def updated_at(self) -> datetime:
        _updated_at = self._updated_at
        dt = parse_to_dt(_updated_at)
        return dt


class ApplicationUser:

    if TYPE_CHECKING:
        id: int
        slug: str
        node_id: str
        owner: BaseUser
        name: str
        description: str
        external_url: str
        html_url: str
        created_at: datetime
        updated_at: datetime
        permissions: Dict[str, str]
        events: List[str]
        installations_count: int

    def __init__(self, *, state: ApplicationState, data: ApplicationUserPayload):
        self._state = state
        self._update(data)
        
    def _update(self, data: ApplicationUserPayload):
        self.id = data["id"]
        self.slug = data["slug"]
        self.node_id = data["node_id"]
        self.owner = BaseUser(state=self._state, data=data["owner"])
        self.name = data["name"]
        self.description = data["description"]
        self.external_url = data["external_url"]
        self.html_url = data["html_url"]
        self._created_at = data["created_at"]
        self._updated_at = data["updated_at"]
        self.permissions = data["permissions"]
        self.events = data["events"]
        self.installations_count = data["installations_count"]

    @property
    def created_at(self) -> datetime:
        _created_at = self._created_at
        dt = datetime.strptime(_created_at, TIMESTAMP_FORMAT)
        return dt

    @property
    def updated_at(self) -> datetime:
        _updated_at = self._updated_at
        dt = datetime.strptime(_updated_at, TIMESTAMP_FORMAT)
        return dt
    