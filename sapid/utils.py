from __future__ import annotations

from datetime import datetime
from typing import (
    Any,
    List,
    Optional,
    Union,
    Coroutine,
    TYPE_CHECKING
)

import jwt

if TYPE_CHECKING:
    from .state import ApplicationState


def generate_jwt(payload: dict, key: str, headers: dict, algorithm: str = "RS256"):
    token = jwt.encode(
        payload=payload,
        key=key,
        algorithm=algorithm,
        headers=headers
    )

    return token

TIMESTAMP_FORMAT = "YYYY-MM-DDTHH:MM:SSZ"

def parse_to_dt(text: str, _format: str = TIMESTAMP_FORMAT):
    return None # this function is broken. for now we will return None
    return datetime.strptime(text, _format)

def safe_convert(_type: type, _data, *args, **kwargs):
    # a function to convert raw data into a python object.
    # its 'safe' as it will handle data being None.
    if _data is None:
        return None
    
    return _type(*args, **kwargs)

def _parse_list_to_object(_object_type: type, *, state: ApplicationState, data: List[dict], kwargs = {}) -> list:
    _os = []
    for item in data:
        try:
            obj = _object_type(state=state, data=data, **kwargs)
        except Exception:
            continue
        _os.append(obj)

    return _os

class Cacheable:
    """An abc that adds a cache to each class.
    """
    __mutable_cache__ = {}

    def set_cache(self, key: Any, value: Any):
        self.__mutable_cache__[key] = value

    def get_cache(self, key: Any):
        return self.__mutable_cache__.get(key)

NUMSTR = Union[str, int]
PAYLOADITEMTYPE = Union[str, bool, list, int]

class EventListener:
    def __init__(
        self,
        event_name: str,
        callback: Coroutine,
        *,
        check: Optional[Coroutine] = None
    ):
        self.event_name = event_name
        self.callback = callback
        self.check = check

    async def call(self, *args):
        if self.check is not None:
            success = await self.check(*args)
            if success is False:
                raise RuntimeError("Check failed")
            
        return await self.callback(*args)
    