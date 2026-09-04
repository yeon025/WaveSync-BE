from typing import List

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models.user_echo import UserEcho


def save_all(db: Session, echoes: List[UserEcho]) -> None:
    # 커밋은 호출부 책임
    db.add_all(echoes)


def soft_delete_by_user_resonator_ids(db: Session, ids: List[int]) -> None:
    stmt = (
        update(UserEcho)
        .where(UserEcho.user_resonator_id.in_(ids), UserEcho.is_deleted.is_(False))
        .values(is_deleted=True)
    )
    db.execute(stmt)
