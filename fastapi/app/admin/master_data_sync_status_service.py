from typing import Dict, List

from sqlalchemy.orm import Session

from app.admin import master_data_sync_status_repository
from app.admin.schemas import SyncResult, SyncTarget


def record_success(db: Session, results: Dict[str, SyncResult]) -> None:
    for target, result in results.items():
        master_data_sync_status_repository.upsert(db, target, success=True, result=result, error_message=None)
    db.commit()


def record_failure(db: Session, targets: List[SyncTarget], error_message: str) -> None:
    # sync()가 어느 대상에서 멈췄는지 호출부는 알 수 없으므로, 이 요청에 포함된 대상 전체를 실패로
    # 남긴다 — 프론트가 대상 하나씩 요청을 보내는 한 사실상 한 개뿐이다.
    db.rollback()
    for target in targets:
        master_data_sync_status_repository.upsert(db, target.value, success=False, result=None, error_message=error_message)
    db.commit()
