from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.resonator.master.weapon_master import WeaponMaster


def find_by_name_without_spaces(db: Session, name: str) -> Optional[WeaponMaster]:
    return db.scalar(select(WeaponMaster).where(func.replace(WeaponMaster.name, " ", "") == name))
