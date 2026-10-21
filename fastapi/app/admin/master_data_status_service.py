from typing import Dict

from sqlalchemy.orm import Session

from app.admin import master_data_sync_status_repository
from app.admin.schemas import MasterDataStatusItem, MasterDataStatusResponse, SyncResult, SyncTarget
from app.resonator.master import resonator_master_repository, weapon_master_repository
from app.resonator.resonance_node import resonance_node_master_repository
from app.storage.object_storage_factory import get_object_storage_service


def get_status(db: Session) -> MasterDataStatusResponse:
    counts = _get_counts(db)
    sync_rows = master_data_sync_status_repository.find_all(db)

    items: Dict[str, MasterDataStatusItem] = {}

    for target in SyncTarget:
        row = sync_rows.get(target.value)

        items[target.value] = MasterDataStatusItem(
            count=counts[target],
            lastSyncedAt=row.synced_at if row is not None else None,
            lastSyncSuccess=row.success if row is not None else None,
            lastSyncResult=(
                SyncResult(created=row.created, updated=row.updated, unchanged=row.unchanged, skipped=row.skipped)
                if row is not None and row.success
                else None
            ),
            lastSyncError=row.error_message if row is not None and not row.success else None,
        )

    return MasterDataStatusResponse(items=items)


def _get_counts(db: Session) -> Dict[SyncTarget, int]:
    # echoes는 echo_master 같은 별도 테이블이 없다 — Encore 아이콘을 echo_bucket에 직접 올리는
    # 구조(master_data_sync_service.sync_echoes)라서, 오브젝트 스토리지에 쌓인 파일 수로 대신한다.
    # standing_images도 별도 테이블이 아니라 resonator_master.standing_image 컬럼 보유 여부다.
    storage = get_object_storage_service()

    return {
        SyncTarget.RESONATORS: resonator_master_repository.count_all(db),
        SyncTarget.WEAPONS: weapon_master_repository.count_all(db),
        SyncTarget.RESONANCE_NODES: resonance_node_master_repository.count_all(db),
        SyncTarget.ECHOES: len(storage.list_objects(storage.echo_bucket)),
        SyncTarget.STANDING_IMAGES: resonator_master_repository.count_with_standing_image(db),
    }
