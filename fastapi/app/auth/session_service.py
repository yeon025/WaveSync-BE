import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.auth import rate_limiter, user_identity_repository, user_repository, user_session_repository
from app.auth.authenticated_user import AuthenticatedUser
from app.auth.user_role import UserRole
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode

_SESSION_TTL = timedelta(days=180)
_REFRESH_THRESHOLD = timedelta(days=30)


def hash_token(raw_token: str) -> str:
    # google_login_service도 세션 조회에 같은 해시를 쓰므로 공개 함수로 둔다.
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _maybe_extend_expiry(db: Session, session) -> bool:
    now = datetime.now(timezone.utc)
    if session.expires_at - now >= _REFRESH_THRESHOLD:
        return False

    user_session_repository.extend_expiry(db, session.id, now + _SESSION_TTL)
    return True


def get_user_by_token(db: Session, raw_token: Optional[str]) -> Optional[AuthenticatedUser]:
    if not raw_token:
        return None

    row = user_session_repository.find_active_with_user(db, hash_token(raw_token))
    if row is None:
        return None

    session, user = row
    # commit 전에 응답에 쓸 값을 확보한다 (commit은 인스턴스를 expire시킨다).
    authenticated_user = AuthenticatedUser(id=user.id, role=user.role)

    if _maybe_extend_expiry(db, session):
        db.commit()

    return authenticated_user


def classify_invalid_token(db: Session, raw_token: Optional[str]) -> str:
    # iPhone Safari 세션 유지 이슈 진단용 — 인증 로직에는 영향을 주지 않고 UNAUTHORIZED 사유만 분류한다.
    # 원인 확정 후 제거한다.
    if not raw_token:
        return "cookie_missing"

    session = user_session_repository.find_by_token_hash(db, hash_token(raw_token))
    if session is None:
        return "session_invalid"
    if session.revoked_at is not None:
        return "session_revoked"
    if session.expires_at <= datetime.now(timezone.utc):
        return "session_expired"
    return "session_invalid"  # find_active_with_user와 조건이 어긋나는 경우(이론상 도달하지 않음)


def issue_session_for_user(db: Session, user_id: int, role: UserRole) -> Tuple[AuthenticatedUser, str]:
    # 커밋은 호출부 책임 — issue_or_reuse_session과 google_login_service가 공유한다.
    new_raw_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + _SESSION_TTL
    user_session_repository.create_session(db, user_id, hash_token(new_raw_token), expires_at)

    return AuthenticatedUser(id=user_id, role=role), new_raw_token


def issue_or_reuse_session(
    db: Session, raw_token: Optional[str], client_key: str
) -> Tuple[AuthenticatedUser, Optional[str]]:
    existing_user = get_user_by_token(db, raw_token)
    if existing_user is not None:
        return existing_user, None

    if not rate_limiter.allow_new_session(client_key):
        raise CustomException(ErrorCode.TOO_MANY_REQUESTS)

    user = user_repository.create_user(db)
    db.flush()  # 세션 행을 만들려면 user.id가 먼저 필요하다.

    authenticated_user, new_raw_token = issue_session_for_user(db, user.id, user.role)
    db.commit()

    return authenticated_user, new_raw_token


def revoke_by_token(db: Session, raw_token: Optional[str]) -> None:
    if not raw_token:
        return

    row = user_session_repository.find_active_with_user(db, hash_token(raw_token))
    if row is None:
        return

    session, _user = row
    user_session_repository.revoke(db, session.id)
    db.commit()


def is_guest(db: Session, user_id: int) -> bool:
    # user_identities에 연결된 행이 없으면 아직 로그인 수단이 없는 게스트다.
    return not user_identity_repository.exists_for_user(db, user_id)
