import os
import secrets
from typing import Optional, Tuple

from fastapi import Request, Response

_OAUTH_STATE_COOKIE_NAME = "wavesync_oauth_state"
_OAUTH_STATE_MAX_AGE_SECONDS = 10 * 60  # 로그인 리다이렉트 왕복 시간만 버티면 되므로 10분으로 충분하다.
_OAUTH_STATE_PATH = "/api/auth/google"
_SEPARATOR = ":"  # state/nonce 둘 다 secrets.token_urlsafe라 콜론과 겹치지 않는다.


def _is_prod() -> bool:
    return os.getenv("APP_ENV") == "prod"


def issue_oauth_state(response: Response) -> Tuple[str, str]:
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)

    response.set_cookie(
        key=_OAUTH_STATE_COOKIE_NAME,
        value=f"{state}{_SEPARATOR}{nonce}",
        max_age=_OAUTH_STATE_MAX_AGE_SECONDS,
        httponly=True,
        secure=_is_prod(),
        # 세션 쿠키와 달리 우리 백엔드로 되돌아오는 same-site 리다이렉트 요청에만 필요해 lax로 충분하다.
        samesite="lax",
        path=_OAUTH_STATE_PATH,
    )

    return state, nonce


def pop_oauth_state(request: Request, response: Response) -> Optional[Tuple[str, str]]:
    # 재사용(중복 요청)을 막기 위해 읽는 즉시 쿠키를 지운다 — 1회용.
    raw = request.cookies.get(_OAUTH_STATE_COOKIE_NAME)
    response.delete_cookie(key=_OAUTH_STATE_COOKIE_NAME, path=_OAUTH_STATE_PATH)

    if not raw or _SEPARATOR not in raw:
        return None

    state, nonce = raw.split(_SEPARATOR, 1)
    if not state or not nonce:
        return None

    return state, nonce
