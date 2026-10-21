import os
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode

_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
_TIMEOUT_SECONDS = 10
_SCOPE = "openid email profile"

# google-auth가 공식 지원하는 iat/exp 검증용 시계 오차 허용치(초). 서버와 Google 서버 간 NTP 오차로
# "Token used too early"가 나는 것을 막는 용도이며, 5초를 넘기지 않는다(ID 토큰 수명은 보통 1시간이라
# 이 정도 허용은 재생 공격 창을 사실상 넓히지 않는다). signature/iss/aud/nonce 검증에는 영향이 없다.
_CLOCK_SKEW_TOLERANCE_SECONDS = 5


def _get_client_id() -> Optional[str]:
    return os.getenv("GOOGLE_CLIENT_ID")


def _get_client_secret() -> Optional[str]:
    return os.getenv("GOOGLE_CLIENT_SECRET")


def _get_redirect_uri() -> Optional[str]:
    return os.getenv("GOOGLE_OAUTH_REDIRECT_URI")


def build_authorization_url(state: str, nonce: str) -> str:
    client_id = _get_client_id()
    redirect_uri = _get_redirect_uri()

    # 환경변수 미설정과 실제 실패를 구분하지 않는다 — 설정 상태를 흘리지 않기 위함.
    if not client_id or not redirect_uri:
        logger.error("Google OAuth 환경변수가 설정되지 않아 로그인을 시작할 수 없습니다.")
        raise CustomException(ErrorCode.GOOGLE_LOGIN_FAILED)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": _SCOPE,
        "state": state,
        "nonce": nonce,
        # 재방문자도 매번 계정을 선택할 수 있게 한다 (여러 Google 계정을 쓰는 경우 고려).
        "prompt": "select_account",
    }
    return f"{_AUTHORIZATION_ENDPOINT}?{urlencode(params)}"


def exchange_code_for_tokens(code: str) -> dict:
    client_id = _get_client_id()
    client_secret = _get_client_secret()
    redirect_uri = _get_redirect_uri()

    if not client_id or not client_secret or not redirect_uri:
        logger.error("Google OAuth 환경변수가 설정되지 않아 토큰을 교환할 수 없습니다.")
        raise CustomException(ErrorCode.GOOGLE_LOGIN_FAILED)

    try:
        response = requests.post(
            _TOKEN_ENDPOINT,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        body = e.response.text if e.response is not None else None
        logger.error(f"Google 토큰 교환 실패: {e} (body={body})")
        raise CustomException(ErrorCode.EXTERNAL_API_FAILED)

    return response.json()


def verify_id_token(raw_id_token: str, expected_nonce: str) -> dict:
    client_id = _get_client_id()
    if not client_id:
        logger.error("GOOGLE_CLIENT_ID가 설정되지 않아 ID 토큰을 검증할 수 없습니다.")
        raise CustomException(ErrorCode.GOOGLE_LOGIN_FAILED)

    try:
        # 서명/발급자(iss)/대상(aud)/만료(exp)를 모두 검증한다. nonce는 검증하지 않으므로 아래에서 직접 대조한다.
        # clock_skew_in_seconds는 iat/exp 판정에만 쓰이는 라이브러리 공식 옵션이다.
        claims = google_id_token.verify_oauth2_token(
            raw_id_token,
            google_requests.Request(),
            client_id,
            clock_skew_in_seconds=_CLOCK_SKEW_TOLERANCE_SECONDS,
        )
    except ValueError as e:
        # 예외 메시지에는 토큰이 아니라 iat/exp/now의 유닉스 타임스탬프만 들어 있어 로그에 남겨도 안전하다.
        # 5초 허용 후에도 실패했다면 단순 초 단위 오차가 아니라 서버 시간 자체가 크게 어긋났을 가능성이
        # 높으므로, 우리 쪽 현재 UTC 시각을 같이 남겨 원인을 구분할 수 있게 한다.
        logger.warning(f"Google ID 토큰 검증 실패: {e} (서버 UTC 시각={datetime.now(timezone.utc).isoformat()})")
        raise CustomException(ErrorCode.GOOGLE_LOGIN_FAILED)

    if claims.get("nonce") != expected_nonce:
        logger.warning("Google ID 토큰의 nonce가 일치하지 않습니다.")
        raise CustomException(ErrorCode.GOOGLE_LOGIN_FAILED)

    return claims
