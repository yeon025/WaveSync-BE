from typing import List, Optional
from sqlalchemy import select, exists
from sqlalchemy.orm import Session
from app.models.resonator_master import ResonatorMaster
from app.models.user_resonator import UserResonator
from app.schemas.response import ResonatorSummaryResponseDto


def find_by_name(db: Session, name: str) -> Optional[ResonatorMaster]:
    return db.scalar(select(ResonatorMaster).where(ResonatorMaster.name == name))


def exists_by_name(db: Session, name: str) -> bool:
    return db.scalar(
        select(exists().where(ResonatorMaster.name == name))
    )


def find_resonator_summary(db: Session) -> List[ResonatorSummaryResponseDto]:
    # relationship 대신 명시적 JOIN 사용 (ResonatorMaster.user_resonators는 미사용 필드라 안 걸어둠)
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
            (UserResonator.resonator_master_id == ResonatorMaster.id)
            & (UserResonator.is_deleted.is_(False)),
            isouter=True,
        )
    )
    rows = db.execute(stmt).all()

    return [
        ResonatorSummaryResponseDto(
            userResonatorId=row.id,
            resonatorName=row.name,
            rarity=row.rarity,
            releaseVersion=row.release_version,
            thumbnailImageUrl=row.thumbnail_image,
        )
        for row in rows
    ]
