from datetime import datetime, timezone
from typing import Dict, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.admin.master_data_sync_status import MasterDataSyncStatus
from app.admin.schemas import SyncResult


def find_all(db: Session) -> Dict[str, MasterDataSyncStatus]:
    rows = db.scalars(select(MasterDataSyncStatus))
    return {row.target: row for row in rows}


def upsert(
    db: Session,
    target: str,
    success: bool,
    result: Optional[SyncResult],
    error_message: Optional[str],
) -> None:
    # 커밋은 호출부(master_data_sync_status_service) 책임.
    existing = db.get(MasterDataSyncStatus, target)

    if existing is None:
        existing = MasterDataSyncStatus(target=target)
        db.add(existing)

    existing.synced_at = datetime.now(timezone.utc)
    existing.success = success
    existing.created = result.created if result else None
    existing.updated = result.updated if result else None
    existing.unchanged = result.unchanged if result else None
    existing.skipped = result.skipped if result else None
    existing.error_message = error_message
