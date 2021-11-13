from typing import (
    TypedDict,
    Optional,
    Dict,
    List
)


class User(TypedDict, total=False):
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
    created_at: Optional[str]
    updated_at: Optional[str]
    private_gists: Optional[int]
    total_private_repos: Optional[int]
    owned_private_repos: Optional[int]
    disk_usage: Optional[int]
    collaborators: Optional[int]
    two_factor_authentication: Optional[bool]
    gravatar_id: Optional[str]
    plan: Optional[dict]

class ApplicationUser(TypedDict, total=False):
    id: int
    slug: str
    node_id: str
    owner: dict
    name: str
    description: str
    external_url: str
    html_url: str
    created_at: str
    updated_at: str
    permissions: Dict[str, str]
    events: List[str]
    installations_count: int