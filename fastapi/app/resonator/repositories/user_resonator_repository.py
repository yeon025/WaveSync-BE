from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload, selectinload

from app.resonator.models.resonator_master import ResonatorMaster
from app.resonator.models.user_echo import UserEcho
from app.resonator.models.user_resonator import UserResonator


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


def _base_relation_options():
    """resonator_master/weapon_master/final_stat — 전부 to-one 관계라 joinedload 한 번으로
    행 중복 없이 로드된다. find_by_id와 find_by_id_for_update가 동일하게 필요로 하는 이유는
    두 메서드가 우연히 비슷해서가 아니라, update_resonator가 조회 후 이 세 관계를 전부
    실제로 읽기 때문이다 (weapon_master.refine_type, final_stat 갱신, resonator_master 기준값)."""
    return (
        joinedload(UserResonator.resonator_master),
        joinedload(UserResonator.weapon_master),
        joinedload(UserResonator.final_stat),
    )


def _echo_relation_options():
    """user_echoes(+user_echo_subs) — 컬렉션은 joinedload 대신 selectinload로 배치 조회
    (부모 행 중복 방지, N+1 방지). user_echo_subs까지 순회하므로 한 단계 더 체이닝한다.
    find_by_id_with_echoes와 find_by_id_for_update가 동일하게 필요로 하는 이유는
    re_calculate_final_stat이 에코 서브옵션까지 순회해 스펙을 재계산하기 때문이다."""
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
    """update_resonator 전용 — 기본 관계(_base_relation_options)와 에코 관계(_echo_relation_options)를
    모두 로드해야 재계산(spec_calculation_service.re_calculate_final_stat)이 추가 쿼리 없이 끝난다.

    이름과 달리 현재 SELECT ... FOR UPDATE 같은 실제 행 잠금은 걸려 있지 않다 (기존 동작 그대로 유지 —
    락 적용 여부는 이번 변경 범위 밖이라 별도로 판단 필요)."""
    stmt = (
        select(UserResonator)
        .options(*_base_relation_options(), *_echo_relation_options())
        .where(UserResonator.id == user_resonator_id, UserResonator.is_deleted.is_(False))
    )
    return db.scalar(stmt)
