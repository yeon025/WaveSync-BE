from typing import Optional
from sqlalchemy import select, exists
from sqlalchemy.orm import Session
from app.models.resonator_master import ResonatorMaster


def find_by_name(db: Session, name: str) -> Optional[ResonatorMaster]:
    return db.scalar(select(ResonatorMaster).where(ResonatorMaster.name == name))


def exists_by_name(db: Session, name: str) -> bool:
    return db.scalar(
        select(exists().where(ResonatorMaster.name == name))
    )
