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
    # relationship 대신 명시적 LEFT JOIN
    # 반환값은 (id, name, rarity, release_version, thumbnail_image) 컬럼을 가진 원시 Row 목록이다.
    # API 응답(ResonatorSummaryResponse) 조립은 서비스 계층 책임이다.
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
