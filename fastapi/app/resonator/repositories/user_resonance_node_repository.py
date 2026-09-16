from typing import List

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.resonator.models.user_resonance_node import UserResonanceNode


def save_all(db: Session, nodes: List[UserResonanceNode]) -> None:
    # 커밋은 호출부 책임
    db.add_all(nodes)


def soft_delete_by_user_resonator_ids(db: Session, ids: List[int]) -> None:
    stmt = (
        update(UserResonanceNode)
        .where(
            UserResonanceNode.user_resonator_id.in_(ids),
            UserResonanceNode.is_deleted.is_(False),
        )
        .values(is_deleted=True)
    )
    db.execute(stmt)
