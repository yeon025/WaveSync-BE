from typing import Optional

from sqlalchemy.orm import Session

from app.admin.schemas import MasterDataItemsResponse, SyncTarget
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.profile_extraction.echo.echo_matching_service import decode_echo_name
from app.resonator.master import resonator_master_repository, weapon_master_repository
from app.resonator.resonance_node import resonance_node_master_repository
from app.storage.object_storage_factory import get_object_storage_service


def get_items(
    db: Session, target: SyncTarget, page: int, page_size: int, search: Optional[str]
) -> MasterDataItemsResponse:
    offset = (page - 1) * page_size

    if target == SyncTarget.RESONATORS:
        items, total = _get_resonator_items(db, search, offset, page_size)
    elif target == SyncTarget.WEAPONS:
        items, total = _get_weapon_items(db, search, offset, page_size)
    elif target == SyncTarget.RESONANCE_NODES:
        items, total = _get_resonance_node_items(db, search, offset, page_size)
    elif target == SyncTarget.ECHOES:
        items, total = _get_echo_items(search, offset, page_size)
    else:
        # STANDING_IMAGES는 별도 테이블이 아니라 resonator_master.standing_image 컬럼일 뿐이라
        # 독립된 상세 목록이 없다.
        raise CustomException(ErrorCode.MASTER_DATA_ITEMS_NOT_SUPPORTED)

    return MasterDataItemsResponse(items=items, page=page, pageSize=page_size, total=total)


def _get_resonator_items(db: Session, search: Optional[str], offset: int, limit: int):
    rows = resonator_master_repository.find_page(db, search, offset, limit)
    total = resonator_master_repository.count_matching(db, search)

    items = [
        {
            "id": r.id,
            "name": r.name,
            "rarity": r.rarity,
            "element": r.element.value,
            "hp": r.hp,
            "attack": r.attack,
            "defense": r.defense,
            "thumbnailImageUrl": r.thumbnail_image,
        }
        for r in rows
    ]
    return items, total


def _get_weapon_items(db: Session, search: Optional[str], offset: int, limit: int):
    rows = weapon_master_repository.find_page(db, search, offset, limit)
    total = weapon_master_repository.count_matching(db, search)

    items = [
        {
            "id": r.id,
            "name": r.name,
            "attackValue": r.attack_value,
            "mainType": r.main_type.value,
            "mainValue": float(r.main_value),
            "refineType": r.refine_type.value if r.refine_type else None,
            "imageUrl": r.image,
        }
        for r in rows
    ]
    return items, total


def _get_resonance_node_items(db: Session, search: Optional[str], offset: int, limit: int):
    rows = resonance_node_master_repository.find_page(db, search, offset, limit)
    total = resonance_node_master_repository.count_matching(db, search)

    items = [
        {
            "id": node.id,
            "resonatorMasterId": node.resonator_master_id,
            "resonatorName": resonator_name,
            "outerNodeType": node.outer_node_type.value,
            "outerTopNodeValue": float(node.outer_top_node_value),
            "outerMiddleNodeValue": float(node.outer_middle_node_value),
            "innerNodeType": node.inner_node_type.value,
            "innerTopNodeValue": float(node.inner_top_node_value),
            "innerMiddleNodeValue": float(node.inner_middle_node_value),
        }
        for node, resonator_name in rows
    ]
    return items, total


def _get_echo_items(search: Optional[str], offset: int, limit: int):
    # echo_master 테이블이 없어(오브젝트 스토리지에 파일만 저장) storage가 전체 목록만 돌려준다.
    # 검색·페이지네이션은 응답을 만들 때 여기서 직접 처리한다 — 응답 자체는 한 페이지만 내려간다.
    storage = get_object_storage_service()
    objects = storage.list_objects(storage.echo_bucket)

    decorated = [{"key": obj.key, "name": decode_echo_name(obj.key), "etag": obj.etag} for obj in objects]

    if search:
        lowered = search.lower()
        decorated = [d for d in decorated if lowered in d["name"].lower()]

    decorated.sort(key=lambda d: d["name"])

    total = len(decorated)
    items = decorated[offset : offset + limit]
    return items, total
