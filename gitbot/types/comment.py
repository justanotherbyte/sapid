from typing import (
    TypedDict,
    Dict,
    Union
)


class Comment(TypedDict, total=False):
    id: int
    node_id: str
    url: str
    html_url: str
    body: str
    user: Dict[str, Union[str, int, bool]]
    created_at: str
    updated_at: str
    issue_url: str
    author_association: str