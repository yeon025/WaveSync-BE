from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload
from app.models.user_resonator import UserResonator
from app.models.resonator_master import ResonatorMaster


def find_ids_by_resonator_name(db: Session, name: str) -> List[int]:
    stmt = (
        select(UserResonator.id)
        .join(ResonatorMaster, UserResonator.resonator_master_id == ResonatorMaster.id)
        .where(ResonatorMaster.name == name, UserResonator.is_deleted.is_(False))
    )
    return list(db.scalars(stmt))


def soft_delete_by_ids(db: Session, ids: List[int]) -> None:
    stmt = (
        update(UserResonator)
        .where(UserResonator.id.in_(ids), UserResonator.is_deleted.is_(False))
        .values(is_deleted=True)
    )
    db.execute(stmt)
    # commit은 호출부(서비스 계층)의 책임 — Spring @Transactional 경계와 동일하게 여기서 커밋하지 않는다


def find_by_id(db: Session, user_resonator_id: int) -> Optional[UserResonator]:
    stmt = (
        select(UserResonator)
        .options(
            joinedload(UserResonator.resonator_master),
            joinedload(UserResonator.weapon_master),
            joinedload(UserResonator.final_stat),
        )
        .where(UserResonator.id == user_resonator_id, UserResonator.is_deleted.is_(False))
    )
    return db.scalar(stmt)


def find_by_id_for_update(db: Session, user_resonator_id: int) -> Optional[UserResonator]:
    stmt = (
        select(UserResonator)
        .options(
            joinedload(UserResonator.resonator_master),
            joinedload(UserResonator.weapon_master),
            joinedload(UserResonator.final_stat),
        )
        .where(UserResonator.id == user_resonator_id, UserResonator.is_deleted.is_(False))
    )
    return db.scalar(stmt)
