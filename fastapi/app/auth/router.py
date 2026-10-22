import os
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth import google_login_service, google_oauth_client, oauth_state, rate_limiter, session_service
from app.auth.authenticated_user import AuthenticatedUser
from app.auth.cookie import SESSION_COOKIE_NAME, clear_session_cookie, set_session_cookie
from app.auth.csrf import require_csrf_header
from app.auth.current_user import get_current_user
from app.auth.schemas import SessionResponse
from app.config.cors import ALLOWED_ORIGINS
from app.config.logger import logger
from app.db.session import get_db
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.schemas.api_response import ApiResponse

router = APIRouter(prefix="/auth")

# OAuth 콜백에서만 쓰는 프런트엔드 오류 전달 쿼리 파라미터. 값은 아래 허용 목록의 ErrorCode.code만
# 들어간다(메시지·스택 트레이스·토큰 등은 절대 포함하지 않는다).
_LOGIN_ERROR_QUERY_PARAM = "login_error"

# 콜백 처리 중 예상 가능한 실패만 프런트로 리다이렉트한다. 그 외(DB 오류 등 내부 오류)는 기존처럼
# JSON 예외 응답으로 남겨 서버 로그에서 추적한다.
_CALLBACK_REDIRECTABLE_ERROR_CODES = {
    ErrorCode.OAUTH_STATE_INVALID.value[1],
    ErrorCode.GOOGLE_LOGIN_FAILED.value[1],
    ErrorCode.GOOGLE_ACCOUNT_ALREADY_LINKED.value[1],
    ErrorCode.EXTERNAL_API_FAILED.value[1],
    ErrorCode.TOO_MANY_REQUESTS.value[1],
}


def _append_login_error(base_url: str, error_code: str) -> str:
    parts = urlsplit(base_url)
    query = dict(parse_qsl(parts.query))
    query[_LOGIN_ERROR_QUERY_PARAM] = error_code
    return urlunsplit(parts._replace(query=urlencode(query)))


def _frontend_redirect_url() -> str:
    # 새 환경변수를 무조건 신뢰하지 않고, CORS/CSRF가 이미 쓰는 허용 출처 목록에 속하는지 검증한다.
    url = os.getenv("GOOGLE_OAUTH_SUCCESS_REDIRECT_URL")
    if not url or not any(url.startswith(origin) for origin in ALLOWED_ORIGINS):
        logger.error("GOOGLE_OAUTH_SUCCESS_REDIRECT_URL이 설정되지 않았거나 허용된 출처가 아닙니다.")
        raise CustomException(ErrorCode.GOOGLE_LOGIN_FAILED)
    return url


@router.post(
    "/session",
    response_model=ApiResponse[SessionResponse],
    response_model_exclude_none=True,
    status_code=200,
    dependencies=[Depends(require_csrf_header)],
)
def issue_session(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_token = request.cookies.get(SESSION_COOKIE_NAME)
    client_key = rate_limiter.get_client_key(request.headers.get("X-Forwarded-For"), request.client.host)

    user, new_raw_token = session_service.issue_or_reuse_session(db, raw_token, client_key)

    if new_raw_token:
        set_session_cookie(response, new_raw_token)

    # iPhone Safari 세션 유지 이슈 진단용 로그 — 쿠키 값/토큰은 남기지 않는다. 원인 확정 후 제거한다.
    logger.info(
        f"세션 발급 처리 | cookie_present={raw_token is not None} | new_session_issued={new_raw_token is not None} | "
        f"origin={request.headers.get('Origin')} | user_agent={request.headers.get('User-Agent')}"
    )

    is_guest = session_service.is_guest(db, user.id)
    return ApiResponse(
        code="OK", message="세션을 확인했습니다.", data=SessionResponse.from_authenticated_user(user, is_guest)
    )


@router.get(
    "/session",
    response_model=ApiResponse[SessionResponse],
    response_model_exclude_none=True,
    status_code=200,
)
def get_session(current_user: AuthenticatedUser = Depends(get_current_user), db: Session = Depends(get_db)):
    is_guest = session_service.is_guest(db, current_user.id)
    return ApiResponse(
        code="OK",
        message="현재 세션을 조회했습니다.",
        data=SessionResponse.from_authenticated_user(current_user, is_guest),
    )


@router.delete(
    "/session",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    status_code=200,
    dependencies=[Depends(require_csrf_header)],
)
def revoke_session(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_token = request.cookies.get(SESSION_COOKIE_NAME)
    session_service.revoke_by_token(db, raw_token)
    clear_session_cookie(response)

    return ApiResponse(code="OK", message="세션을 종료했습니다.")


@router.get("/google/login")
def google_login():
    # 쿠키를 최종 응답(RedirectResponse)에 직접 심어야 한다 — Depends(Response)에 set_cookie하면
    # 반환값이 별도 Response 인스턴스일 때 그 헤더가 복사되지 않는다.
    redirect = RedirectResponse(url="about:blank", status_code=302)
    state, nonce = oauth_state.issue_oauth_state(redirect)
    redirect.headers["location"] = google_oauth_client.build_authorization_url(state, nonce)
    return redirect


@router.get("/google/callback")
def google_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
):
    frontend_url = _frontend_redirect_url()
    redirect = RedirectResponse(url=frontend_url, status_code=302)
    state_pair = oauth_state.pop_oauth_state(request, redirect)
    cookie_state, cookie_nonce = state_pair if state_pair else (None, None)

    try:
        if error or not code or not state:
            raise CustomException(ErrorCode.GOOGLE_LOGIN_FAILED)

        existing_raw_token = request.cookies.get(SESSION_COOKIE_NAME)
        client_key = rate_limiter.get_client_key(request.headers.get("X-Forwarded-For"), request.client.host)

        _user, new_raw_token = google_login_service.login_with_google(
            db, code, state, cookie_state, cookie_nonce, existing_raw_token, client_key
        )
    except CustomException as exc:
        # 예상 가능한 로그인 실패만 프런트로 리다이렉트한다. 새 세션 발급도, 기존 세션 폐기도 하지
        # 않는다(실패 지점까지의 모든 변경은 commit 전이라 db.close()에서 그대로 버려진다).
        if exc.code not in _CALLBACK_REDIRECTABLE_ERROR_CODES:
            raise
        logger.warning(f"Google OAuth 콜백 실패: {exc.code}")
        redirect.headers["location"] = _append_login_error(frontend_url, exc.code)
        return redirect

    set_session_cookie(redirect, new_raw_token)

    return redirect
