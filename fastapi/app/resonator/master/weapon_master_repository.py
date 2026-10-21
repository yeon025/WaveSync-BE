from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.resonator.master.weapon_master import WeaponMaster


def find_by_name_without_spaces(db: Session, name: str) -> Optional[WeaponMaster]:
    return db.scalar(select(WeaponMaster).where(func.replace(WeaponMaster.name, " ", "") == name))


def _search_condition(search: Optional[str]):
    if not search:
        return None
    conditions = [WeaponMaster.name.ilike(f"%{search}%")]
    if search.isdigit():
        conditions.append(WeaponMaster.id == int(search))
    return or_(*conditions)


def find_all_by_ids(db: Session, ids: List[int]) -> List[WeaponMaster]:
    if not ids:
        return []
    return list(db.scalars(select(WeaponMaster).where(WeaponMaster.id.in_(ids))))


def count_all(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(WeaponMaster))


def find_page(db: Session, search: Optional[str], offset: int, limit: int) -> List[WeaponMaster]:
    stmt = select(WeaponMaster).order_by(WeaponMaster.id)
    condition = _search_condition(search)
    if condition is not None:
        stmt = stmt.where(condition)
    return list(db.scalars(stmt.offset(offset).limit(limit)))


def count_matching(db: Session, search: Optional[str]) -> int:
    stmt = select(func.count()).select_from(WeaponMaster)
    condition = _search_condition(search)
    if condition is not None:
        stmt = stmt.where(condition)
    return db.scalar(stmt)
