from typing import List

from sqlalchemy.orm import Session

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.resonator import spec_calculation_service
from app.resonator.master import resonator_master_repository
from app.resonator.resonance_node.branch_position import BranchPosition
from app.resonator.resonance_node.node_position import NodePosition
from app.resonator.resonance_node.resonance_node_mapper import get_stat
from app.resonator.schemas import (
    EchoDetail,
    EchoListResponse,
    ResonanceNode,
    ResonatorDetailResponse,
    ResonatorSettingResponse,
    ResonatorStat,
    ResonatorSummaryResponse,
    UpdateResonatorRequest,
    WeaponDetail,
    WeaponSetting,
)
from app.resonator.user_resonator import user_resonator_repository
from app.storage.object_storage_factory import get_object_storage_service


def get_resonator_summary(db: Session) -> List[ResonatorSummaryResponse]:
    rows = resonator_master_repository.find_resonator_summary(db)

    resonators = [
        ResonatorSummaryResponse(
            userResonatorId=row.id,
            resonatorName=row.name,
            rarity=row.rarity,
            releaseVersion=row.release_version,
            thumbnailImageUrl=row.thumbnail_image,
        )
        for row in rows
    ]

    # 현대 한글은 코드포인트 순서가 사전순과 같다 (숫자/영문이 섞인 이름이 추가되면 재검토).
    resonators.sort(key=lambda r: (-r.releaseVersion, r.resonatorName))

    storage = get_object_storage_service()
    for resonator in resonators:
        resonator.thumbnailImageUrl = storage.create_url(resonator.thumbnailImageUrl)

    return resonators


def get_resonator_detail(db: Session, user_resonator_id: int) -> ResonatorDetailResponse:
    user_resonator = user_resonator_repository.find_by_id(db, user_resonator_id)
    if user_resonator is None:
        raise CustomException(ErrorCode.RESONATOR_NOT_FOUND)

    storage = get_object_storage_service()
    standing_image_url = storage.create_url(user_resonator.resonator_master.standing_image)
    weapon_image_url = storage.create_url(user_resonator.weapon_master.image)

    weapon = WeaponDetail.from_user_resonator(user_resonator, weapon_image_url)
    stat = ResonatorStat.from_final_stat(user_resonator.final_stat)

    return ResonatorDetailResponse(
        userResonatorId=user_resonator.id,
        resonatorName=user_resonator.resonator_master.name,
        element=user_resonator.resonator_master.element.value,
        standingImageUrl=standing_image_url,
        resonanceChainLevel=user_resonator.resonance_chain_level,
        weapon=weapon,
        stat=stat,
    )


def get_resonator_setting(db: Session, user_resonator_id: int) -> ResonatorSettingResponse:
    user_resonator = user_resonator_repository.find_by_id(db, user_resonator_id)
    if user_resonator is None:
        raise CustomException(ErrorCode.RESONATOR_NOT_FOUND)
    logger.debug("공명자 조회를 완료했습니다.")

    # find_by_id가 노드 관계는 eager load하지 않아 쿼리가 2번 추가된다 (N+1 아님).
    node_master = user_resonator.resonator_master.resonance_node_master
    logger.debug("공명 노드 조회를 완료했습니다.")

    nodes = [
        ResonanceNode(
            branchPosition=node.branch_position,
            nodePosition=node.node_position,
            active=node.is_active,
            stat=get_stat(node_master, node.branch_position, node.node_position),
        )
        for node in user_resonator.user_resonance_nodes
    ]
    logger.debug("조회한 공명 노드를 dto로 변환했습니다.")

    storage = get_object_storage_service()
    weapon_image_url = storage.create_url(user_resonator.weapon_master.image)
    logger.debug("이미지를 전체 경로로 변환했습니다.")

    weapon = WeaponSetting.from_user_resonator(user_resonator, weapon_image_url)
    logger.debug("무기 조회 후 dto로 변환했습니다.")

    return ResonatorSettingResponse(nodes=nodes, weapon=weapon)


def get_resonator_echoes(db: Session, user_resonator_id: int) -> EchoListResponse:
    user_resonator = user_resonator_repository.find_by_id_with_echoes(db, user_resonator_id)
    if user_resonator is None:
        raise CustomException(ErrorCode.RESONATOR_NOT_FOUND)

    storage = get_object_storage_service()
    echoes = [
        EchoDetail.from_user_echo(echo, storage.create_url(echo.image) if echo.image else None)
        for echo in user_resonator.user_echoes
    ]
    return EchoListResponse(echoes=echoes, echoAnalysis=user_resonator.echo_analysis)


def update_resonator(db: Session, user_resonator_id: int, data: UpdateResonatorRequest) -> None:
    user_resonator = user_resonator_repository.find_by_id_for_update(db, user_resonator_id)
    if user_resonator is None:
        raise CustomException(ErrorCode.RESONATOR_NOT_FOUND)

    node_map = {f"{node.branchPosition.value}_{node.nodePosition.value}": node for node in data.nodes}

    required_keys = {
        f"{branch_position.value}_{node_position.value}"
        for branch_position in BranchPosition
        for node_position in NodePosition
    }
    missing_keys = required_keys - node_map.keys()
    if missing_keys:
        logger.warning(f"업데이트 요청에 누락된 공명 노드 위치가 있습니다. missing={sorted(missing_keys)}")
        raise CustomException(ErrorCode.VALIDATION_FAILED)

    required_type = {node.stat.type for node in data.nodes if node.stat is not None and node.stat.type is not None}

    refine_type = user_resonator.weapon_master.refine_type
    if refine_type is not None:
        required_type.add(refine_type)

    spec_calculation_service.re_calculate_final_stat(required_type, user_resonator, data.nodes, data.weaponRefineLevel)

    user_resonator.refine_level = data.weaponRefineLevel

    # 위에서 10개 위치를 모두 검증했으므로 바로 인덱싱한다.
    for node in user_resonator.user_resonance_nodes:
        key = f"{node.branch_position.value}_{node.node_position.value}"
        node.is_active = node_map[key].active

    db.commit()


def delete_resonator(db: Session, user_resonator_ids: List[int]) -> None:
    user_resonator_repository.soft_delete_by_ids(db, user_resonator_ids)
    db.commit()
