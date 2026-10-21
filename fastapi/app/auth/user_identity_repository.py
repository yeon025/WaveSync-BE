from typing import Optional, Tuple

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.auth.user import User
from app.auth.user_identity import AuthProvider, UserIdentity


def create(db: Session, user_id: int, provider: AuthProvider, provider_user_id: str) -> UserIdentity:
    # 커밋은 호출부(google_login_service) 책임.
    identity = UserIdentity(user_id=user_id, provider=provider, provider_user_id=provider_user_id)
    db.add(identity)
    return identity


def find_by_provider_and_subject(
    db: Session, provider: AuthProvider, provider_user_id: str
) -> Optional[Tuple[UserIdentity, User]]:
    stmt = (
        select(UserIdentity, User)
        .join(User, User.id == UserIdentity.user_id)
        .where(UserIdentity.provider == provider, UserIdentity.provider_user_id == provider_user_id)
    )
    return db.execute(stmt).first()


def exists_for_user(db: Session, user_id: int) -> bool:
    stmt = select(exists().where(UserIdentity.user_id == user_id))
    return bool(db.scalar(stmt))
