from typing import List

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.final_stat import FinalStat


def save(db: Session, final_stat: FinalStat) -> FinalStat:
    # Spring JpaRepository.save() 대응. 커밋은 호출부 책임
    db.add(final_stat)
    return final_stat


def delete_by_user_resonator_ids(db: Session, ids: List[int]) -> None:
    # 소프트 삭제 아님 — FinalStat엔 is_deleted 컬럼이 없어 진짜 DELETE
    stmt = delete(FinalStat).where(FinalStat.user_resonator_id.in_(ids))
    db.execute(stmt)
    # 커밋은 호출부(서비스 계층) 책임 — 다른 repository들과 동일 원칙
