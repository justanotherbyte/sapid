from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse

class SapidException(Exception):
    """A Custom base exception that all errors raised by the sapid library will raise"""
    pass

class HTTPException(SapidException):
    def __init__(self, data: dict, response: ClientResponse):
        self.data = data
        self.response = response

    def __str__(self) -> str:
        reason = self.response.reason
        code = self.response.status
        msg = self.data.get("message", "No Message")
        docs = self.data.get("documentation_url", "unspecified")
        
        fmt = "{code}: {reason}: {msg}: {docs}"
        return fmt.format(reason=reason, code=code, msg=msg, docs=docs)