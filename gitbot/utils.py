import jwt


def generate_jwt(payload: dict, key: str, headers: dict, algorithm: str = "RS256"):
    token = jwt.encode(
        payload=payload,
        key=key,
        algorithm=algorithm,
        headers=headers
    )

    return token

TIMESTAMP_FORMAT = "YYYY-MM-DDTHH:MM:SSZ"