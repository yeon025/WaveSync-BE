import os
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.auth import (
    google_oauth_client,
    rate_limiter,
    session_service,
    user_identity_repository,
    user_repository,
    user_session_repository,
)
from app.auth.authenticated_user import AuthenticatedUser
from app.auth.user_identity import AuthProvider
from app.auth.user_role import UserRole
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode


def _normalize_email(email: Optional[str]) -> str:
    return (email or "").strip().lower()


def _resolve_role(claims: dict) -> UserRole:
    # 관리자 권한은 별도 클레임 키 없이, 매 Google 로그인마다 서버가 서명까지 검증한 ID 토큰의
    # email/email_verified 클레임만으로 결정한다. 클라이언트가 보낸 값은 아예 읽지 않으므로
    # role을 임의로 주장할 방법이 없다.
    admin_email = os.getenv("ADMIN_EMAIL")
    if not admin_email:
        return UserRole.USER

    if not claims.get("email_verified"):
        return UserRole.USER

    if _normalize_email(claims.get("email")) == _normalize_email(admin_email):
        return UserRole.ADMIN

    return UserRole.USER


def login_with_google(
    db: Session,
    code: str,
    query_state: str,
    cookie_state: Optional[str],
    cookie_nonce: Optional[str],
    existing_raw_token: Optional[str],
    client_key: str,
) -> Tuple[AuthenticatedUser, str]:
    # state는 콜백 URL을 그대로 재사용하는 공격을 막는 1회용 CSRF 토큰이다. Google을 호출하기 전에 검증한다.
    if not cookie_state or not cookie_nonce or query_state != cookie_state:
        raise CustomException(ErrorCode.OAUTH_STATE_INVALID)

    tokens = google_oauth_client.exchange_code_for_tokens(code)
    raw_id_token = tokens.get("id_token")
    if not raw_id_token:
        raise CustomException(ErrorCode.GOOGLE_LOGIN_FAILED)

    claims = google_oauth_client.verify_id_token(raw_id_token, cookie_nonce)
    subject = claims.get("sub")
    if not subject:
        raise CustomException(ErrorCode.GOOGLE_LOGIN_FAILED)

    resolved_role = _resolve_role(claims)

    # session_service.get_user_by_token은 만료 연장 시 커밋하므로 쓰지 않는다 — 이 함수 전체를 단일
    # 트랜잭션(끝에서 한 번만 commit)으로 묶기 위해 리포지토리를 직접 조회한다.
    existing_session, existing_user = (None, None)
    if existing_raw_token:
        row = user_session_repository.find_active_with_user(db, session_service.hash_token(existing_raw_token))
        if row is not None:
            existing_session, existing_user = row

    found = user_identity_repository.find_by_provider_and_subject(db, AuthProvider.GOOGLE, subject)

    if found is not None:
        _, user = found
        if existing_user is not None and existing_user.id != user.id and session_service.is_guest(db, existing_user.id):
            # 순수 게스트 세션(자체 데이터를 갖고 있을 수 있음)이 이미 다른 계정에 연결된 Google
            # 계정으로 로그인하려는 상황 — 자동으로 합치면 게스트 데이터에 다시 접근할 수 없게
            # 되므로, 임의로 버리지 않고 명확한 오류로 막는다.
            raise CustomException(ErrorCode.GOOGLE_ACCOUNT_ALREADY_LINKED)
        target_user_id = user.id
    elif existing_user is not None and session_service.is_guest(db, existing_user.id):
        # 식별자 없는 순수 게스트가 로그인하는 첫 시도 — 데이터 이전이 아니라 같은 user_id에 식별자만 연결한다.
        target_user_id = existing_user.id
        user_identity_repository.create(db, target_user_id, AuthProvider.GOOGLE, subject)
    else:
        # 게스트 세션이 없거나(새 기기 등) 이미 다른 식별자가 연결된 세션이면 새 계정을 만든다.
        if not rate_limiter.allow_new_session(client_key):
            raise CustomException(ErrorCode.TOO_MANY_REQUESTS)

        new_user = user_repository.create_user(db)
        db.flush()  # user_identities가 참조할 user.id가 먼저 필요하다.
        target_user_id = new_user.id
        user_identity_repository.create(db, target_user_id, AuthProvider.GOOGLE, subject)

    # 매 로그인마다 현재 ADMIN_EMAIL 기준으로 역할을 다시 반영한다 — 전에 admin이었어도 더 이상
    # 일치하지 않으면 여기서 즉시 user로 내려가, 권한이 영구히 남는 경로를 없앤다.
    user_repository.set_role(db, target_user_id, resolved_role)

    if existing_session is not None:
        # 세션 고정 공격 방지 — 로그인 성공 시 이전 세션(게스트든 아니든)은 폐기하고 새로 발급한다.
        user_session_repository.revoke(db, existing_session.id)

    authenticated_user, new_raw_token = session_service.issue_session_for_user(db, target_user_id, resolved_role)
    db.commit()

    return authenticated_user, new_raw_token
