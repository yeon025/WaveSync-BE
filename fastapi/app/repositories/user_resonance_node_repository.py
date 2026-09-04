from typing import List

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.user_resonance_node import UserResonanceNode


def save_all(db: Session, nodes: List[UserResonanceNode]) -> None:
    # 커밋은 호출부 책임
    db.add_all(nodes)


def find_all_by_user_resonator_id(db: Session, user_resonator_id: int) -> List[UserResonanceNode]:
    stmt = (
        select(UserResonanceNode)
        .where(
            UserResonanceNode.user_resonator_id == user_resonator_id,
            UserResonanceNode.is_deleted.is_(False),
        )
        .order_by(UserResonanceNode.branch_position, UserResonanceNode.node_position)
    )
    return list(db.scalars(stmt))


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
