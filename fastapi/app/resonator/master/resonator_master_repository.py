from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from app.resonator.master.resonator_master import ResonatorMaster
from app.resonator.user_resonator.user_resonator import UserResonator


def find_by_name(db: Session, name: str) -> Optional[ResonatorMaster]:
    return db.scalar(select(ResonatorMaster).where(ResonatorMaster.name == name))


def find_by_name_without_spaces(db: Session, name: str) -> Optional[ResonatorMaster]:
    return db.scalar(select(ResonatorMaster).where(func.replace(ResonatorMaster.name, " ", "") == name))


def _search_condition(search: Optional[str]):
    if not search:
        return None
    conditions = [ResonatorMaster.name.ilike(f"%{search}%")]
    if search.isdigit():
        conditions.append(ResonatorMaster.id == int(search))
    return or_(*conditions)


def count_all(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(ResonatorMaster))


def count_with_standing_image(db: Session) -> int:
    return db.scalar(
        select(func.count()).select_from(ResonatorMaster).where(ResonatorMaster.standing_image.isnot(None))
    )


def find_page(db: Session, search: Optional[str], offset: int, limit: int) -> List[ResonatorMaster]:
    stmt = select(ResonatorMaster).order_by(ResonatorMaster.id)
    condition = _search_condition(search)
    if condition is not None:
        stmt = stmt.where(condition)
    return list(db.scalars(stmt.offset(offset).limit(limit)))


def count_matching(db: Session, search: Optional[str]) -> int:
    stmt = select(func.count()).select_from(ResonatorMaster)
    condition = _search_condition(search)
    if condition is not None:
        stmt = stmt.where(condition)
    return db.scalar(stmt)


def find_all_by_ids(db: Session, ids: List[int]) -> List[ResonatorMaster]:
    if not ids:
        return []
    return list(db.scalars(select(ResonatorMaster).where(ResonatorMaster.id.in_(ids))))


def find_all(db: Session) -> List[ResonatorMaster]:
    return list(db.scalars(select(ResonatorMaster)))


def find_resonator_summary(db: Session, user_id: int) -> List[Row]:
    # user_id 조건은 WHERE가 아니라 JOIN 조건에 둔다 — WHERE에 두면 아직 등록하지 않은 마스터
    # 캐릭터 행(LEFT JOIN으로 userResonatorId=None을 내려주는 행)까지 결과에서 사라져 버린다.
    #
    # 정렬은 희귀도 내림차순(5성 먼저) 후 이름순이다. name은 COLLATE "C"로 고정해 DB의 로캘
    # 설정과 무관하게 바이트(=코드포인트) 순서로 정렬한다 — 현대 한글은 코드포인트 순서가
    # 사전순과 같다(숫자/영문이 섞인 이름이 추가되면 재검토).
    stmt = (
        select(
            UserResonator.id,
            ResonatorMaster.name,
            ResonatorMaster.rarity,
            ResonatorMaster.thumbnail_image,
        )
        .select_from(ResonatorMaster)
        .join(
            UserResonator,
            (UserResonator.resonator_master_id == ResonatorMaster.id)
            & (UserResonator.user_id == user_id)
            & (UserResonator.is_deleted.is_(False)),
            isouter=True,
        )
        .order_by(ResonatorMaster.rarity.desc(), ResonatorMaster.name.collate("C"))
    )
    return db.execute(stmt).all()
