import jwt

from datetime import datetime


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