from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.resonator.models.resonator_damage_master import ResonatorDamageMaster


def find_by_resonator_master_id(db: Session, resonator_master_id: int) -> Optional[ResonatorDamageMaster]:
    # 점수 계산 대상이 아닌 공명자는 행이 없으므로 None이 정상 결과다.
    stmt = select(ResonatorDamageMaster).where(ResonatorDamageMaster.resonator_master_id == resonator_master_id)
    return db.scalar(stmt)
