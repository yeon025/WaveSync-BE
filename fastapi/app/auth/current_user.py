from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.auth import session_service
from app.auth.authenticated_user import AuthenticatedUser
from app.auth.cookie import SESSION_COOKIE_NAME
from app.auth.csrf import require_csrf_header
from app.auth.user_role import UserRole
from app.config.logger import logger
from app.db.session import get_db
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    _csrf: None = Depends(require_csrf_header),
) -> AuthenticatedUser:
    raw_token = request.cookies.get(SESSION_COOKIE_NAME)
    user = session_service.get_user_by_token(db, raw_token)
    if user is None:
        # iPhone Safari 세션 유지 이슈 진단용 로그 — 쿠키 값/토큰은 남기지 않는다. 원인 확정 후 제거한다.
        reason = session_service.classify_invalid_token(db, raw_token)
        logger.warning(
            f"세션 인증 실패 | reason={reason} | path={request.url.path} | "
            f"origin={request.headers.get('Origin')} | user_agent={request.headers.get('User-Agent')}"
        )
        raise CustomException(ErrorCode.UNAUTHORIZED)
    return user


def require_admin(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    if current_user.role != UserRole.ADMIN:
        raise CustomException(ErrorCode.FORBIDDEN)
    return current_user
