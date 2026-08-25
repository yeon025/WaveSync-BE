from typing import List
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.models.user_resonance_node import UserResonanceNode


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
    # 커밋은 호출부(서비스 계층) 책임 — user_resonator_repository.soft_delete_by_ids와 동일 원칙
