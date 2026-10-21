from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.auth import session_service
from app.auth.authenticated_user import AuthenticatedUser
from app.auth.cookie import SESSION_COOKIE_NAME
from app.auth.csrf import require_csrf_header
from app.auth.user_role import UserRole
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
        raise CustomException(ErrorCode.UNAUTHORIZED)
    return user


def require_admin(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    if current_user.role != UserRole.ADMIN:
        raise CustomException(ErrorCode.FORBIDDEN)
    return current_user
