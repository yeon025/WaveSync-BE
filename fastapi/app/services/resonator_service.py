from decimal import Decimal
from typing import List

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.mapper.resonance_node_mapper import get_stat
from app.models.branch_position import BranchPosition
from app.models.node_position import NodePosition
from app.models.stat_type import StatType
from app.models.user_echo import UserEcho
from app.models.user_echo_sub import UserEchoSub
from app.models.user_resonance_node import UserResonanceNode
from app.models.user_resonator import UserResonator
from app.repositories import (
    final_stat_repository,
    resonator_master_repository,
    user_echo_repository,
    user_echo_sub_repository,
    user_resonance_node_repository,
    user_resonator_repository,
    weapon_master_repository,
)
from app.schemas.common import ResonanceNode, ResonatorStat, WeaponDetail, WeaponSetting
from app.schemas.request import UpdateResonatorRequest
from app.schemas.response import (
    CreateResonatorResponse,
    ResonatorDetailResponse,
    ResonatorSettingResponse,
    ResonatorSummaryResponse,
)
from app.services import extract_profile_validation_service, spec_calculation_service
from app.services.object_storage_factory import get_object_storage_service
from app.services.resonator_profile_service import extract_info

# Spring service.ResonatorService 대응.


def get_resonator_summary(db: Session) -> List[ResonatorSummaryResponse]:
    resonators = resonator_master_repository.find_resonator_summary(db)

    # Spring은 Collator.getInstance(Locale.KOREAN)으로 정렬한다. 여기서는 별도 ICU
    # 의존성을 추가하지 않고 파이썬 기본 문자열 비교를 쓴다 — 현대 한글 음절
    # (U+AC00~U+D7A3)은 유니코드 코드포인트 순서가 사전식 순서와 사실상 일치해서
    # 이 데이터셋(순수 한글 공명자 이름)엔 결과가 동일하다. (의도적 차이 — 완료 보고 참고)
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
        element=user_resonator.resonator_master.element.code,
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

    # find_by_id는 resonator_master/weapon_master/final_stat만 eager loading한다
    # (Spring의 findById도 동일 — resonanceNodeMaster/userResonanceNodes는 지연 로딩).
    # 단건 상세 조회라 N+1이 아니라 이 요청 안에서 정확히 쿼리 2번(resonance_node_master,
    # user_resonance_nodes)만 추가로 발생 — Spring/Hibernate와 쿼리 횟수가 동일하다.
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


def create_resonator(db: Session, resonator_profile: UploadFile) -> CreateResonatorResponse:
    # 공명자 프로필 이미지 저장
    storage = get_object_storage_service()
    profile_url = storage.upload_profile_image(resonator_profile)
    logger.debug(f"{profile_url} 저장을 완료했습니다.")

    # 인프로세스 OCR 호출 (Spring의 FastApiClient HTTP 호출 대응 — 같은 프로세스라
    # 네트워크 왕복 없이 직접 호출한다. DATA_NOT_FOUND는 이 경로에선 발생하지 않는다)
    logger.info("이미지 추출을 시작합니다.")
    extracted = extract_info(profile_url)
    logger.info("이미지 추출이 완료되었습니다.")

    # 검증
    validated_weapon_name = extract_profile_validation_service.validate(db, extracted)

    # 이름을 기준으로 DB 조회 (Spring처럼 null 체크 없음 — validate()가 존재를 이미 보장)
    rm = resonator_master_repository.find_by_name(db, extracted.resonatorName)
    wm = weapon_master_repository.find_by_name(db, validated_weapon_name)
    rnm = rm.resonance_node_master
    logger.debug("추출된 데이터로 데이터베이스 조회를 완료했습니다.")

    # 저장 전에 동일한 공명자는 삭제
    target_ids = user_resonator_repository.find_ids_by_resonator_name(db, extracted.resonatorName)
    if target_ids:
        logger.debug(f"조회한 id: {target_ids}")
        _delete(db, target_ids)
        logger.debug("동일한 공명자 정보를 삭제했습니다.")

    # UserResonator 객체 생성 후 저장
    user_resonator = UserResonator(
        resonance_chain_level=extracted.resonanceChainLevel,
        refine_level=1,
        resonator_master=rm,
        weapon_master=wm,
    )
    user_resonator_repository.save(db, user_resonator)

    # UserResonanceNode 객체 생성 후 저장 (BranchPosition x NodePosition = 10개)
    # is_active=True를 명시한다 — Column(default=True)는 DB flush 시점에만 적용되고
    # 바로 아래에서 flush 전 메모리 상태를 읽어 nodes_dto를 만들기 때문에
    # (Spring @Builder.Default는 생성 시점에 즉시 적용되는 것과 대응)
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
    user_resonance_node_repository.save_all(db, user_resonance_nodes)

    # 노드를 dto로 변환
    nodes = [
        ResonanceNode(
            branchPosition=node.branch_position,
            nodePosition=node.node_position,
            active=node.is_active,
            stat=get_stat(rnm, node.branch_position, node.node_position),
        )
        for node in user_resonance_nodes
    ]

    # Echo 객체 생성
    user_echoes: List[UserEcho] = []
    user_echo_subs: List[UserEchoSub] = []

    for echo_dto in extracted.echoes:
        echo = UserEcho(
            main_type=StatType.from_code(echo_dto.main.type),
            main_value=Decimal(str(echo_dto.main.value)),
            secondary_type=StatType.from_code(echo_dto.secondary.type),
            secondary_value=int(echo_dto.secondary.value),
            # relationship로 생성 — back_populates가 user_resonator.user_echoes에 자동 반영
            user_resonator=user_resonator,
        )
        user_echoes.append(echo)

        for sub_dto in echo_dto.subs:
            sub = UserEchoSub(
                type=StatType.from_code(sub_dto.type),
                value=Decimal(str(sub_dto.value)),
                # relationship로 생성 — back_populates가 echo.user_echo_subs에 자동 반영
                user_echo=echo,
            )
            user_echo_subs.append(sub)

    # UserEcho, UserEchoSub 저장
    user_echo_repository.save_all(db, user_echoes)
    user_echo_sub_repository.save_all(db, user_echo_subs)

    # 최종 스펙 계산 (user_resonator.user_echoes는 위 back_populates로 이미 채워져 있음)
    final_stat = spec_calculation_service.calculate_final_stat(user_resonator, nodes)

    # 최종 스펙을 DB에 저장
    final_stat_repository.save(db, final_stat)
    logger.debug("최종 스펙을 데이터베이스에 저장했습니다.")

    return CreateResonatorResponse(resonatorName=rm.name)


def update_resonator(db: Session, user_resonator_id: int, data: UpdateResonatorRequest) -> None:
    # id로 userResonator 조회
    user_resonator = user_resonator_repository.find_by_id_for_update(db, user_resonator_id)
    if user_resonator is None:
        raise CustomException(ErrorCode.RESONATOR_NOT_FOUND)

    node_map = {f"{node.branchPosition.value}_{node.nodePosition.value}": node for node in data.nodes}

    # Spring 원본엔 없는 방어 로직 — 10개 위치가 요청에 전부 없으면 아래 루프에서
    # 조용히 실패하는 대신 여기서 명확히 거부한다. 누락 위치는 로그에 남긴다.
    required_keys = {
        f"{branch_position.value}_{node_position.value}"
        for branch_position in BranchPosition
        for node_position in NodePosition
    }
    missing_keys = required_keys - node_map.keys()
    if missing_keys:
        logger.warning(f"업데이트 요청에 누락된 공명 노드 위치가 있습니다. missing={sorted(missing_keys)}")
        raise CustomException(ErrorCode.VALIDATION_FAILED)

    # 10개의 공명 노드에서 모든 StatType 수집
    required_type = {node.stat.type for node in data.nodes if node.stat is not None and node.stat.type is not None}

    # 무기의 재련 옵션 추가
    refine_type = user_resonator.weapon_master.refine_type
    if refine_type is not None:
        required_type.add(refine_type)

    # 스펙 재계산
    spec_calculation_service.re_calculate_final_stat(required_type, user_resonator, data.nodes, data.weaponRefineLevel)

    # 무기 재련 레벨 변경
    user_resonator.refine_level = data.weaponRefineLevel

    # 공명 노드 활성화 상태 변경 (완전성 검증을 이미 통과했으므로 직접 인덱싱)
    for node in user_resonator.user_resonance_nodes:
        key = f"{node.branch_position.value}_{node.node_position.value}"
        node.is_active = node_map[key].active


def _delete(db: Session, user_resonator_ids: List[int]) -> None:
    """Spring ResonatorService.delete(ids) 대응. commit/rollback 없음 — 호출자의
    트랜잭션 경계에 속한다 (delete_resonator, create_resonator가 공유)."""
    user_resonator_repository.soft_delete_by_ids(db, user_resonator_ids)
    user_resonance_node_repository.soft_delete_by_user_resonator_ids(db, user_resonator_ids)
    user_echo_repository.soft_delete_by_user_resonator_ids(db, user_resonator_ids)
    user_echo_sub_repository.soft_delete_by_user_resonator_ids(db, user_resonator_ids)
    final_stat_repository.delete_by_user_resonator_ids(db, user_resonator_ids)


def delete_resonator(db: Session, user_resonator_ids: List[int]) -> None:
    _delete(db, user_resonator_ids)
