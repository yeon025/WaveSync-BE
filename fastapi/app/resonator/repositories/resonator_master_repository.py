from typing import List, Optional

from sqlalchemy import exists, select
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from app.resonator.models.resonator_master import ResonatorMaster
from app.resonator.models.user_resonator import UserResonator


def find_by_name(db: Session, name: str) -> Optional[ResonatorMaster]:
    return db.scalar(select(ResonatorMaster).where(ResonatorMaster.name == name))


def exists_by_name(db: Session, name: str) -> bool:
    return db.scalar(select(exists().where(ResonatorMaster.name == name)))


def find_resonator_summary(db: Session) -> List[Row]:
    stmt = (
        select(
            UserResonator.id,
            ResonatorMaster.name,
            ResonatorMaster.rarity,
            ResonatorMaster.release_version,
            ResonatorMaster.thumbnail_image,
        )
        .select_from(ResonatorMaster)
        .join(
            UserResonator,
            (UserResonator.resonator_master_id == ResonatorMaster.id) & (UserResonator.is_deleted.is_(False)),
            isouter=True,
        )
    )
    return db.execute(stmt).all()
