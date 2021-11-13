from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse

class GitBotException(Exception):
    """A Custom base exception that all errors raised by the GitBot library will raise"""
    pass

class HTTPException(GitBotException):
    def __init__(self, data: dict, response: ClientResponse):
        self.data = data
        self.response = response

    def __str__(self) -> str:
        reason = self.response.reason
        status = self.response.status
        msg = self.data.get("message", "No Message")

        return "{status} {reason} {msg}".format(
            status=status,
            reason=reason,
            msg=msg
        )