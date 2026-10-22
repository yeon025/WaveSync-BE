from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.auth.user import User
from app.auth.user_session import UserSession


def create_session(db: Session, user_id: int, token_hash: str, expires_at: datetime) -> UserSession:
    # 커밋은 호출부(session_service) 책임.
    session = UserSession(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(session)
    return session


def find_by_token_hash(db: Session, token_hash: str) -> Optional[UserSession]:
    # 진단 로그용 — revoked/expires_at 조건 없이 토큰 해시 존재 여부만 확인한다.
    stmt = select(UserSession).where(UserSession.token_hash == token_hash)
    return db.execute(stmt).scalar_one_or_none()


def find_active_with_user(db: Session, token_hash: str) -> Optional[Tuple[UserSession, User]]:
    stmt = (
        select(UserSession, User)
        .join(User, User.id == UserSession.user_id)
        .where(
            UserSession.token_hash == token_hash,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > func.now(),
        )
    )
    return db.execute(stmt).first()


def extend_expiry(db: Session, session_id: int, candidate_expires_at: datetime) -> None:
    # 조건부 UPDATE 1번으로 처리해, 동시 요청이 와도 만료 시간이 뒤로 가는 일이 없게 한다.
    # 커밋은 호출부 책임.
    db.execute(
        update(UserSession)
        .where(UserSession.id == session_id, UserSession.expires_at < candidate_expires_at)
        .values(expires_at=candidate_expires_at)
    )


def revoke(db: Session, session_id: int) -> None:
    # 커밋은 호출부 책임.
    db.execute(update(UserSession).where(UserSession.id == session_id).values(revoked_at=func.now()))
