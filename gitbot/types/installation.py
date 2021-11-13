from typing import (
    TypedDict,
    Dict,
    Union,
    List,
    Optional
)


class Installation(TypedDict):
    id: int
    account: Dict[str, Union[str, int, bool]]
    repository_selection: str
    access_tokens_url: str
    repositories_url: str
    html_url: str
    app_id: int
    app_slug: str
    target_type: str
    permissions: Dict[str, str]
    events: List[str]
    created_at: str
    updated_at: str
    has_multiple_files: bool
    suspended_by: Optional[dict]
    suspended_at: Optional[str]
