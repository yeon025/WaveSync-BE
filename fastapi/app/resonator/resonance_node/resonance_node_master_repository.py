from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from app.resonator.master.resonator_master import ResonatorMaster
from app.resonator.resonance_node.resonance_node_master import ResonanceNodeMaster


def _search_condition(search: Optional[str]):
    if not search:
        return None
    # resonance_node_master엔 이름이 없으므로 조인한 공명자 이름으로, 숫자면 노드 자신의 id로도 찾는다.
    conditions = [ResonatorMaster.name.ilike(f"%{search}%")]
    if search.isdigit():
        conditions.append(ResonanceNodeMaster.id == int(search))
    return or_(*conditions)


def find_all_by_resonator_master_ids(db: Session, resonator_master_ids: List[int]) -> List[ResonanceNodeMaster]:
    if not resonator_master_ids:
        return []
    return list(
        db.scalars(select(ResonanceNodeMaster).where(ResonanceNodeMaster.resonator_master_id.in_(resonator_master_ids)))
    )


def count_all(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(ResonanceNodeMaster))


# resonance_node_master 자체엔 이름이 없어 상세 목록에서는 resonator_master.name을 조인해 함께 보여준다.
def find_page(db: Session, search: Optional[str], offset: int, limit: int) -> List[Row]:
    stmt = (
        select(ResonanceNodeMaster, ResonatorMaster.name)
        .join(ResonatorMaster, ResonanceNodeMaster.resonator_master_id == ResonatorMaster.id)
        .order_by(ResonanceNodeMaster.id)
    )
    condition = _search_condition(search)
    if condition is not None:
        stmt = stmt.where(condition)
    return list(db.execute(stmt.offset(offset).limit(limit)).all())


def count_matching(db: Session, search: Optional[str]) -> int:
    stmt = (
        select(func.count())
        .select_from(ResonanceNodeMaster)
        .join(ResonatorMaster, ResonanceNodeMaster.resonator_master_id == ResonatorMaster.id)
    )
    condition = _search_condition(search)
    if condition is not None:
        stmt = stmt.where(condition)
    return db.scalar(stmt)
