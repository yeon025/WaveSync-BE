import os

from fastapi import Response

SESSION_COOKIE_NAME = "wavesync_session"

_SESSION_MAX_AGE_SECONDS = 180 * 24 * 60 * 60  # 180일


def _is_prod() -> bool:
    return os.getenv("APP_ENV") == "prod"


def set_session_cookie(response: Response, token: str) -> None:
    is_prod = _is_prod()
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=_SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=is_prod,
        # 로컬 개발은 프런트(localhost:3000)와 백엔드(localhost:8000)가 포트만 다른 same-site라 lax로
        # 충분하다. 운영은 프런트(resocollector.com)와 백엔드 도메인이 서로 다른 사이트라 none이 필요하다.
        samesite="none" if is_prod else "lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
