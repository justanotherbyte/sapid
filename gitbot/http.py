import asyncio
import json
import time
from typing import (
    Optional,
    Dict,
    Union,
    Any
)

import aiohttp

from .utils import generate_jwt
from .errors import HTTPException


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
    def __init__(self, pem_fp: str, app_id: str, client_secret: str):
        self.app_id = app_id
        self.client_secret = client_secret

        with open(pem_fp, "r") as f:
            text = f.read()

        self.private_key = text

class HTTPClient:
    def __init__(
        self,
        auth_info: AuthInfo,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        session: Optional[aiohttp.ClientSession] = None
    ):
        self.loop = loop or asyncio.get_event_loop()

        self.__auth = auth_info
        self.__session = session

    def recreate(self):
        if self.__session is None or self.__session.closed is True:
            self.__session = aiohttp.ClientSession()

    async def close(self):
        if self.__session:
            if self.__session.closed is False:
                await self.__session.close()

    async def request_jwt(self, route: Route, **kwargs) -> Union[dict, str, bytes]:
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
                "Authorization": "Bearer {}".format(jwt)
            }
        else:
            kwargs["headers"]["Authorization"] = "Bearer {}".format(jwt)

        async with self.__session.request(method, url, **kwargs) as resp:
            data = await json_or_text(resp)
            if resp.ok:
                return data
            
            raise RuntimeError(str(data))

    def fetch_app(self):
        route = Route("GET", "/app")
        return self.request_jwt(route)


