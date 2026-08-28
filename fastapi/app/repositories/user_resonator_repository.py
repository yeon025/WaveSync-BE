from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.resonator_master import ResonatorMaster
from app.models.user_echo import UserEcho
from app.models.user_resonator import UserResonator


def save(db: Session, user_resonator: UserResonator) -> UserResonator:
    # Spring JpaRepository.save() 대응. commit은 호출부(서비스 계층) 책임 — 다른
    # repository 함수들과 동일 원칙. relationship으로 연결된 자식(예: FinalStat,
    # UserResonanceNode)은 SQLAlchemy의 기본 save-update cascade로 같은 flush에
    # 함께 반영된다.
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
            # selectinload 사용 이유: Spring 원본이 SELECT DISTINCT를 쓴 건 컬렉션을
            # JOIN FETCH하면 부모 행이 자식 수만큼 중복되기 때문 — joinedload로 컬렉션을
            # 물면 같은 문제가 재발하므로, 별도 IN 쿼리로 배치 조회하는 selectinload를 쓴다
            # (CLAUDE.md N+1 방지 원칙과도 부합). SpecCalculationService가 각 UserEcho의
            # user_echo_subs까지 순회하므로 한 단계 더 체이닝해서 배치 조회한다
            # (안 하면 UserEcho 개수만큼 지연 로딩되는 진짜 N+1이 발생함)
            selectinload(UserResonator.user_echoes).selectinload(UserEcho.user_echo_subs),
        )
        .where(UserResonator.id == user_resonator_id, UserResonator.is_deleted.is_(False))
    )
    return db.scalar(stmt)
