from decimal import Decimal
from typing import List

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.profile_extraction.profile_extraction_service import extract_info
from app.resonator import echo_score_service, extract_profile_validation_service, spec_calculation_service
from app.resonator.models.branch_position import BranchPosition
from app.resonator.models.node_position import NodePosition
from app.resonator.models.stat_type import StatType
from app.resonator.models.user_echo import UserEcho
from app.resonator.models.user_echo_sub import UserEchoSub
from app.resonator.models.user_resonance_node import UserResonanceNode
from app.resonator.models.user_resonator import UserResonator
from app.resonator.repositories import resonator_master_repository, user_resonator_repository
from app.resonator.resonance_node_mapper import get_stat
from app.resonator.schemas import (
    CreateResonatorResponse,
    EchoDetail,
    ResonanceNode,
    ResonatorDetailResponse,
    ResonatorSettingResponse,
    ResonatorStat,
    ResonatorSummaryResponse,
    UpdateResonatorRequest,
    WeaponDetail,
    WeaponSetting,
)
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


def get_resonator_echoes(db: Session, user_resonator_id: int) -> List[EchoDetail]:
    user_resonator = user_resonator_repository.find_by_id_with_echoes(db, user_resonator_id)
    if user_resonator is None:
        raise CustomException(ErrorCode.RESONATOR_NOT_FOUND)

    storage = get_object_storage_service()
    return [
        EchoDetail.from_user_echo(echo, storage.create_url(echo.image) if echo.image else None)
        for echo in user_resonator.user_echoes
    ]


def create_resonator(db: Session, resonator_profile: UploadFile) -> CreateResonatorResponse:
    storage = get_object_storage_service()
    profile_url = storage.upload(storage.profile_bucket, resonator_profile)
    logger.debug(f"{profile_url} 저장을 완료했습니다.")

    logger.info("이미지 추출을 시작합니다.")
    extracted = extract_info(profile_url)
    logger.info("이미지 추출이 완료되었습니다.")

    rm, wm = extract_profile_validation_service.validate(db, extracted)
    rnm = rm.resonance_node_master
    logger.debug("추출된 데이터로 데이터베이스 조회를 완료했습니다.")

    # 같은 공명자를 다시 등록하면 기존 데이터를 대체한다.
    target_ids = user_resonator_repository.find_ids_by_resonator_name(db, extracted.resonatorName)
    if target_ids:
        logger.debug(f"조회한 id: {target_ids}")
        user_resonator_repository.soft_delete_by_ids(db, target_ids)
        logger.debug("동일한 공명자 정보를 삭제했습니다.")

    user_resonator = UserResonator(
        resonance_chain_level=extracted.resonanceChainLevel,
        refine_level=1,
        resonator_master=rm,
        weapon_master=wm,
    )

    # Column default는 flush 때 적용되는데 flush 전에 dto를 만들므로 is_active를 명시한다.
    user_resonance_nodes = [
        UserResonanceNode(
            branch_position=branch_position,
            node_position=node_position,
            is_active=True,
            user_resonator=user_resonator,
        )
        for branch_position in BranchPosition
        for node_position in NodePosition
    ]

    nodes = [
        ResonanceNode(
            branchPosition=node.branch_position,
            nodePosition=node.node_position,
            active=node.is_active,
            stat=get_stat(rnm, node.branch_position, node.node_position),
        )
        for node in user_resonance_nodes
    ]

    for echo_dto in extracted.echoes:
        echo = UserEcho(
            name=echo_dto.name,
            image=echo_dto.imagePath,
            main_type=StatType.from_code(echo_dto.main.type),
            main_value=Decimal(str(echo_dto.main.value)),
            secondary_type=StatType.from_code(echo_dto.secondary.type),
            secondary_value=int(echo_dto.secondary.value),
            user_resonator=user_resonator,
        )

        for sub_dto in echo_dto.subs:
            UserEchoSub(
                type=StatType.from_code(sub_dto.type),
                value=Decimal(str(sub_dto.value)),
                user_echo=echo,  # back_populates로 자동 반영
            )

    user_resonator.final_stat = spec_calculation_service.calculate_final_stat(user_resonator, nodes)

    # 자식을 모두 연결한 뒤 저장해야 cascade로 함께 INSERT된다.
    user_resonator_repository.save(db, user_resonator)
    logger.debug("공명자 정보를 데이터베이스에 저장했습니다.")

    # autoflush=False라 flush해야 점수 계산의 재조회에 에코가 잡힌다.
    db.flush()
    echo_score_service.compute_and_persist_echo_scores(db, user_resonator.id)
    logger.debug("에코 점수를 계산했습니다.")

    # commit이 인스턴스를 expire시키므로 응답에 쓸 값은 미리 확보한다.
    resonator_name = rm.name

    # 응답 전에 커밋해야 실패 시 클라이언트가 성공 응답을 받지 않는다.
    db.commit()
    logger.debug("공명자 등록 트랜잭션을 커밋했습니다.")

    return CreateResonatorResponse(resonatorName=resonator_name)


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
