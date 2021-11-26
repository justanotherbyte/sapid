import asyncio
import logging
import json
import time
import sys
from typing import (
    Optional,
    Dict,
    Union,
    Any,
    List
)

import aiohttp

from .utils import generate_jwt
from .enums import IssueLockReason
from .errors import HTTPException


_log = logging.getLogger(__name__)

async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding='utf-8')
    try:
        if response.headers['Content-Type'].startswith('application/json'):
            return json.loads(text)
    except KeyError:
        # Thanks Cloudflare. Thanks discord.py :(
        pass

    return text

class Route:
    BASE = "https://api.github.com"
    def __init__(self, method: str, endpoint: str, **params):
        self.method = method
        self.url = self.BASE + endpoint.format(**params)
        self.endpoint = endpoint

class AuthInfo:
    def __init__(self, pem_fp: str, app_id: str, client_secret: str, client_id: str):
        self.app_id = app_id
        self.client_secret = client_secret

        with open(pem_fp, "r") as f:
            text = f.read()

        self.private_key = text
        self.client_id = client_id

class HTTPClient:
    def __init__(
        self,
        auth_info: AuthInfo,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        session: Optional[aiohttp.ClientSession] = None
    ):
        from . import __version__
        self.loop = loop or asyncio.get_event_loop()

        self.__auth = auth_info
        self.__session = session

        user_agent = 'GithubApplication (https://github.com/justanotherbyte/sapid {0}) Python/{1[0]}.{1[1]} aiohttp/{2}' # taken from discord.py. Their header format is nice.
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    def recreate(self):
        if self.__session is None or self.__session.closed is True:
            self.__session = aiohttp.ClientSession()

    async def close(self):
        if self.__session:
            if self.__session.closed is False:
                await self.__session.close()

    async def request_with_jwt(self, route: Route, **kwargs) -> Union[dict, str, bytes]:
        method = route.method
        url = route.url

        _custom_headers = {}
        _custom_json = {}
        jwt = None

        if "json" in kwargs:
            _custom_json = kwargs["json"]

        if "headers" in kwargs:
            _custom_headers = kwargs["headers"]

        epoch = int(time.time())
        iat = epoch - 60
        exp = epoch + (10 * 60) # 10 minute expiry.

        _custom_json["iss"] = self.__auth.app_id
        _custom_json["iat"] = iat
        _custom_json["exp"] = exp

        jwt = generate_jwt(
            payload=_custom_json,
            key=self.__auth.private_key,
            headers=_custom_headers
        )

        if "headers" not in kwargs:
            kwargs["headers"] = {
                "Authorization": "Bearer {}".format(jwt),
                "User-Agent": self.user_agent
            }
        else:
            kwargs["headers"]["Authorization"] = "Bearer {}".format(jwt)
            kwargs["headers"]["User-Agent"] = self.user_agent

        _log.debug("Making a %s request with JWT to %s" % (method, url))

        async with self.__session.request(method, url, **kwargs) as resp:
            data = await json_or_text(resp)
            if resp.ok:
                return data
            
            raise HTTPException(data, resp)

    async def request(self, route: Route, **kwargs) -> dict:
        method = route.method
        url = route.url
        _apply_secret_auth = kwargs.pop("_apply_secret_auth", False)

        # header creation
        _custom_headers = kwargs.pop("headers", {})
        _custom_auth = _custom_headers.get("Authorization")
        if _custom_auth and _apply_secret_auth:
            raise ValueError("_custom_auth and _apply_secret_auth cannot both be used.")
        
        headers = {
            "accept": "application/vnd.github.v3+json",
            "User-Agent": self.user_agent
        }
        if _custom_auth:
            headers["Authorization"] = _custom_auth
        if _apply_secret_auth is True:
            headers["Authorization"] = "token " + self.__auth.client_secret
        kwargs["headers"] = headers
        print(kwargs)
        
        _log.debug("Making a %s request to %s" % (method, url))
        async with self.__session.request(method, url, **kwargs) as resp:
            data = await json_or_text(resp)
            if resp.ok:
                return data
            
            raise HTTPException(data, resp)

    def fetch_app(self):
        route = Route("GET", "/app")
        return self.request_with_jwt(route)

    def fetch_installations(self):
        route = Route("GET", "/app/installations")
        return self.request_with_jwt(route)

    def fetch_repo_installation(self, owner: str, repo: str):
        route = Route(
            "GET",
            "/repos/{owner}/{repo}/installation",
            owner=owner, repo=repo
        )
        return self.request_with_jwt(route)

    def fetch_access_token(self, installation_id: int):
        installation_id = str(installation_id)
        route = Route(
            "POST",
            "/app/installations/{installation}/access_tokens",
            installation=installation_id
        )
        return self.request_with_jwt(route)

    def fetch_repository_contributors(self, owner: str, repo: str):
        route = Route(
            "GET",
            "/repos/{owner}/{repo}/contributors",
            owner=owner, repo=repo
        )
        return self.request(route)

    def fetch_installations(self):
        route = Route(
            "GET",
            "/app/installations"
        )
        return self.request_with_jwt(route)

    # issues
    def fetch_all_issues(self):
        route = Route("GET", "/issues")
        return self.request(route, _apply_secret_auth=True)

    def fetch_issue(self, owner: str, repo: str, issue_number: int):
        issue_number = str(issue_number)
        route = Route(
            "GET",
            "/repos/{owner}/{repo}/issues/{issue_number}",
            owner=owner, repo=repo, issue_number=issue_number
        )
        return self.request(route)

    def lock_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        access_token: str,
        reason: Optional[IssueLockReason] = None
    ):
        issue_number = str(issue_number)

        _payload = None
        if reason:
            reason = reason.value
            _payload = {
                "lock_reason": reason
            }

        route = Route(
            "PUT",
            "/repos/{owner}/{repo}/issues/{issue_number}/lock",
            owner=owner, repo=repo, issue_number=issue_number
        )
        headers = {}
        if not _payload:
            headers["Content-Length"] = 0

        headers["Authorization"] = "token " + access_token

        if _payload:
            return self.request(route, json=_payload, headers=headers)

        return self.request(route, headers=headers)

    def unlock_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        access_token: str
    ):
        issue_number = str(issue_number)

        route = Route(
            "DELETE",
            "/repos/{owner}/{repo}/issues/{issue_number}/lock",
            owner=owner, repo=repo,
            issue_number=issue_number
        )
        headers = {
            "Authorization": "token " + access_token
        }
        return self.request(route, headers=headers)

    def create_issue(
        self,
        owner: str,
        repo: str,
        access_token: str,
        *,
        title: str,
        body: str,
        assignee: Optional[str] = None,
        milestone: Optional[int] = None,
        labels: List[str] = [],
        assignees: List[str] = []
    ):
        route = Route(
            "POST",
            "/repos/{owner}/{repo}/issues",
            owner=owner, repo=repo
        )

        if assignee and assignees:
            raise ValueError("You cannot pass both `assignee` and `assignees`. Only one may be provided.")

        payload = {
            "title": title,
            "body": body,
            "milestone": milestone,
            "labels": labels,
        }

        if assignees:
            payload["assignees"] = assignees
        elif assignee:
            payload["assignee"] = assignee

        headers = {
            "Authorization": "token " + access_token
        }
        return self.request(route, json=payload, headers=headers)

    def create_issue_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        access_token: str,
        body: str
    ):
        route = Route(
            "POST",
            "/repos/{owner}/{repo}/issues/{issue_number}/comments",
            owner=owner, repo=repo,
            issue_number=issue_number
        )
        payload = {
            "body": body
        }
        headers = {
            "Authorization": "token " + access_token
        }
        return self.request(route, json=payload, headers=headers)

    def fetch_issue_comment(
        self,
        owner: str,
        repo: str,
        comment_id: int
    ):
        comment_id = str(comment_id)
        route = Route(
            "GET",
            "/repos/{owner}/{repo}/issues/comments/{comment_id}",
            owner=owner, repo=repo,
            comment_id=comment_id
        )
        return self.request(route)