from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session, joinedload, selectinload

from app.resonator.models.final_stat import FinalStat
from app.resonator.models.resonator_master import ResonatorMaster
from app.resonator.models.user_echo import UserEcho
from app.resonator.models.user_echo_sub import UserEchoSub
from app.resonator.models.user_resonance_node import UserResonanceNode
from app.resonator.models.user_resonator import UserResonator

# 하위 테이블은 UserResonator 없이 단독으로 다뤄지지 않으므로 저장/삭제도 이 파일에서 함께 처리한다.


def save(db: Session, user_resonator: UserResonator) -> UserResonator:
    """자식을 모두 relationship에 연결한 뒤 호출한다 (add() 이후 연결한 자식은 INSERT되지 않음). 커밋은 호출부 책임."""
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
    """하위 테이블까지 함께 삭제한다. 커밋은 호출부 책임."""
    db.execute(
        update(UserResonator)
        .where(UserResonator.id.in_(ids), UserResonator.is_deleted.is_(False))
        .values(is_deleted=True)
    )
    db.execute(
        update(UserResonanceNode)
        .where(UserResonanceNode.user_resonator_id.in_(ids), UserResonanceNode.is_deleted.is_(False))
        .values(is_deleted=True)
    )
    db.execute(
        update(UserEcho)
        .where(UserEcho.user_resonator_id.in_(ids), UserEcho.is_deleted.is_(False))
        .values(is_deleted=True)
    )
    # UPDATE ... FROM으로 user_echo를 경유한 2단계 JOIN
    db.execute(
        update(UserEchoSub)
        .where(
            UserEchoSub.user_echo_id == UserEcho.id,
            UserEcho.user_resonator_id.in_(ids),
            UserEchoSub.is_deleted.is_(False),
        )
        .values(is_deleted=True)
    )
    # FinalStat엔 is_deleted 컬럼이 없어 하드 DELETE
    db.execute(delete(FinalStat).where(FinalStat.user_resonator_id.in_(ids)))


def _base_relation_options():
    # 전부 to-one 관계라 joinedload로 행 중복 없이 한 번에 로드된다.
    return (
        joinedload(UserResonator.resonator_master),
        joinedload(UserResonator.weapon_master),
        joinedload(UserResonator.final_stat),
    )


def _echo_relation_options():
    # 컬렉션은 부모 행 중복을 피하려고 joinedload 대신 selectinload로 배치 조회한다.
    return (selectinload(UserResonator.user_echoes).selectinload(UserEcho.user_echo_subs),)


def find_by_id(db: Session, user_resonator_id: int) -> Optional[UserResonator]:
    stmt = (
        select(UserResonator)
        .options(*_base_relation_options())
        .where(UserResonator.id == user_resonator_id, UserResonator.is_deleted.is_(False))
    )
    return db.scalar(stmt)


def find_by_id_with_echoes(db: Session, user_resonator_id: int) -> Optional[UserResonator]:
    stmt = (
        select(UserResonator)
        .options(*_echo_relation_options())
        .where(UserResonator.id == user_resonator_id, UserResonator.is_deleted.is_(False))
    )
    return db.scalar(stmt)


def find_by_id_for_update(db: Session, user_resonator_id: int) -> Optional[UserResonator]:
    """이름과 달리 SELECT ... FOR UPDATE 행 잠금은 걸지 않는다 (재계산에 필요한 관계를 모두 로드하는 조회)."""
    stmt = (
        select(UserResonator)
        .options(*_base_relation_options(), *_echo_relation_options())
        .where(UserResonator.id == user_resonator_id, UserResonator.is_deleted.is_(False))
    )
    return db.scalar(stmt)
