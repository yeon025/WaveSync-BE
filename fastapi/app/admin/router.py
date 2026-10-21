from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.admin import (
    master_data_items_service,
    master_data_status_service,
    master_data_sync_service,
    master_data_sync_status_service,
)
from app.admin.schemas import (
    MasterDataItemsResponse,
    MasterDataStatusResponse,
    MasterDataSyncRequest,
    MasterDataSyncResponse,
    SyncTarget,
)
from app.auth.current_user import require_admin
from app.db.session import get_db
from app.exceptions.custom_exception import CustomException
from app.schemas.api_response import ApiResponse

router = APIRouter(prefix="/admin/master-data", dependencies=[Depends(require_admin)])


@router.get(
    "",
    response_model=ApiResponse[MasterDataStatusResponse],
    response_model_exclude_none=True,
    status_code=200,
)
def get_master_data_status(db: Session = Depends(get_db)):
    data = master_data_status_service.get_status(db)

    return ApiResponse(code="OK", message="마스터 데이터 현황을 조회했습니다.", data=data)


@router.get(
    "/{target}/items",
    response_model=ApiResponse[MasterDataItemsResponse],
    response_model_exclude_none=True,
    status_code=200,
)
def get_master_data_items(
    target: SyncTarget,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    data = master_data_items_service.get_items(db, target, page, pageSize, search)

    return ApiResponse(code="OK", message="마스터 데이터 상세를 조회했습니다.", data=data)


@router.post(
    "/sync",
    response_model=ApiResponse[MasterDataSyncResponse],
    response_model_exclude_none=True,
    status_code=200,
)
def sync_master_data(data: MasterDataSyncRequest, db: Session = Depends(get_db)):
    try:
        results = master_data_sync_service.sync(db, data.targets)
    except CustomException as exc:
        # sync()의 기존 로직/커밋 방식은 그대로 두고, 실행 결과만 별도로 기록한다.
        master_data_sync_status_service.record_failure(db, data.targets, exc.message)
        raise

    master_data_sync_status_service.record_success(db, results)

    return ApiResponse(
        code="OK",
        message="마스터 데이터 동기화가 완료되었습니다.",
        data=MasterDataSyncResponse(results=results),
    )
