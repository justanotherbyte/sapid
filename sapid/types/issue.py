from typing import (
    TypedDict,
    Dict,
    List,
    Union,
    Optional
)


class Issue(TypedDict, total=False):
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
    assignee: Optional[Dict[str, Union[str, int]]]
    assignees: List[Optional[Dict[str, Union[str, int]]]]
    comments: int
    created_at: str
    updated_at: str
    closed_at: str
    author_association: str
    body: str
    reactions: Dict[str, Union[str, int]]
    timeline_url: str
    performed_via_github_app: Optional[bool]