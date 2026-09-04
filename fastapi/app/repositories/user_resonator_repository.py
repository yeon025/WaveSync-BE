from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.resonator_master import ResonatorMaster
from app.models.user_echo import UserEcho
from app.models.user_resonator import UserResonator


def save(db: Session, user_resonator: UserResonator) -> UserResonator:
    # 커밋은 호출부 책임. relationship 자식은 기본 save-update cascade로 같은 flush에 반영된다.
    db.add(user_resonator)
    return user_resonator


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
    # 커밋은 호출부 책임


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
            # 컬렉션은 joinedload 대신 selectinload로 배치 조회 (부모 행 중복 방지, N+1 방지).
            # user_echo_subs까지 순회하므로 한 단계 더 체이닝한다.
            selectinload(UserResonator.user_echoes).selectinload(UserEcho.user_echo_subs),
        )
        .where(UserResonator.id == user_resonator_id, UserResonator.is_deleted.is_(False))
    )
    return db.scalar(stmt)
