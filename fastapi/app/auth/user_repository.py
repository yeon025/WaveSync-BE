from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.auth.user import User
from app.auth.user_role import UserRole


def create_user(db: Session) -> User:
    # 커밋은 호출부(session_service) 책임.
    user = User(role=UserRole.USER)
    db.add(user)
    return user


def find_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.scalar(select(User).where(User.id == user_id))


def set_role(db: Session, user_id: int, role: UserRole) -> None:
    # 커밋은 호출부 책임. Google 로그인마다 ADMIN_EMAIL 기준으로 호출되어 role을 승격·강등 모두 반영한다.
    db.execute(update(User).where(User.id == user_id).values(role=role))
