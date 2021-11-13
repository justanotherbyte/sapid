from __future__ import annotations

from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional
)

from .user import BaseUser
from .utils import Cacheable, parse_to_dt, safe_convert

if TYPE_CHECKING:
    from .state import ApplicationState
    from .types.installation import Installation as InstallationPayload


class Installation(Cacheable):

    if TYPE_CHECKING:
        id: int
        account: BaseUser
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
        has_multiple_files: Optional[bool]
        suspended_by: Optional[BaseUser]
        suspended_at: Optional[datetime]

    def __init__(self, *, state: ApplicationState, data: InstallationPayload):
        self._state = state
        self._update(data)

    def _update(self, data: InstallationPayload):
        self.id = data["id"]
        self.account = BaseUser(state=self._state, data=data["account"])
        self.repository_selection = data["repository_selection"]
        self.access_tokens_url = data["access_tokens_url"]
        self.repositories_url = data["repositories_url"]
        self.html_url = data["html_url"]
        self.app_id = data["app_id"]
        self.app_slug = data["app_slug"]
        self.target_type = data["target_type"]
        self.permissions = data["permissions"]
        self.events = data["events"]
        self.created_at = parse_to_dt(data["created_at"])
        self.updated_at = parse_to_dt(data["updated_at"])
        self.has_multiple_files = data.get("has_multiple_files")
        self.suspended_by = safe_convert(
            BaseUser,
            data.get("suspended_by"),
            state=self._state,
            data=data.get("suspended_by")
        )
        self.suspended_at = parse_to_dt(data.get("suspended_at"))