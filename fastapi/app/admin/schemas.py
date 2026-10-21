from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SyncTarget(str, Enum):
    RESONATORS = "resonators"
    WEAPONS = "weapons"
    ECHOES = "echoes"
    RESONANCE_NODES = "resonance_nodes"
    STANDING_IMAGES = "standing_images"


class MasterDataSyncRequest(BaseModel):
    targets: List[SyncTarget] = Field(min_length=1)


class SyncResult(BaseModel):
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    # QualityId/Element 등 알 수 없는 값이라 동기화를 보류한 항목 수.
    skipped: int = 0


class MasterDataSyncResponse(BaseModel):
    results: Dict[str, SyncResult]


class MasterDataStatusItem(BaseModel):
    count: int
    lastSyncedAt: Optional[datetime] = None
    lastSyncSuccess: Optional[bool] = None
    lastSyncResult: Optional[SyncResult] = None
    lastSyncError: Optional[str] = None


class MasterDataStatusResponse(BaseModel):
    items: Dict[str, MasterDataStatusItem]


class MasterDataItemsResponse(BaseModel):
    # 대상(target)마다 컬럼 구성이 전혀 달라(공명자/무기/공명 노드/에코) 공용 타입 모델을 두지 않고
    # 키-값 형태로 내려준다. 어떤 키를 담는지는 master_data_items_service.get_items를 참고.
    items: List[Dict[str, Any]]
    page: int
    pageSize: int
    total: int
