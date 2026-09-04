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


def get_resonator_summary(db: Session) -> List[ResonatorSummaryResponse]:
    resonators = resonator_master_repository.find_resonator_summary(db)

    # 한글 정렬은 파이썬 기본 문자열 비교를 쓴다 (현대 한글은 코드포인트 순서 ≈ 사전순).
    # 숫자/영문이 섞인 이름이 마스터 데이터에 추가되면 재검토 필요.
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

    # find_by_id는 resonator_master/weapon_master/final_stat만 eager load —
    # resonance_node_master / user_resonance_nodes 조회로 쿼리 2번 추가 발생 (N+1 아님).
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
    profile_url = storage.upload(resonator_profile)
    logger.debug(f"{profile_url} 저장을 완료했습니다.")

    # 인프로세스 OCR 호출 (네트워크 왕복 없음)
    logger.info("이미지 추출을 시작합니다.")
    extracted = extract_info(profile_url)
    logger.info("이미지 추출이 완료되었습니다.")

    # 검증
    validated_weapon_name = extract_profile_validation_service.validate(db, extracted)

    # 이름으로 DB 조회 (validate()가 존재를 이미 보장하므로 null 체크 없음)
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

    # 공명 노드 10개 생성 (BranchPosition x NodePosition).
    # is_active=True 명시 — Column(default=True)는 flush 시점에만 적용되는데
    # 아래에서 flush 전 메모리 상태로 dto를 만들기 때문.
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
            user_resonator=user_resonator,  # back_populates로 자동 반영
        )
        user_echoes.append(echo)

        for sub_dto in echo_dto.subs:
            sub = UserEchoSub(
                type=StatType.from_code(sub_dto.type),
                value=Decimal(str(sub_dto.value)),
                user_echo=echo,  # back_populates로 자동 반영
            )
            user_echo_subs.append(sub)

    # UserEcho, UserEchoSub 저장
    user_echo_repository.save_all(db, user_echoes)
    user_echo_sub_repository.save_all(db, user_echo_subs)

    # 최종 스펙 계산 (user_resonator.user_echoes는 back_populates로 이미 채워짐)
    final_stat = spec_calculation_service.calculate_final_stat(user_resonator, nodes)

    # 최종 스펙을 DB에 저장
    final_stat_repository.save(db, final_stat)
    logger.debug("최종 스펙을 데이터베이스에 저장했습니다.")

    # 응답 생성에 필요한 값은 commit 전에 확보한다 (commit이 인스턴스를 expire시키므로).
    resonator_name = rm.name

    # 응답을 만들기 전에 명시적으로 커밋한다 — 여기서 실패하면 라우터를 거쳐
    # SQLAlchemyError 핸들러가 500(DATABASE_ERROR)을 내려주고 클라이언트는 성공 응답을 받지 않는다.
    db.commit()
    logger.debug("공명자 등록 트랜잭션을 커밋했습니다.")

    return CreateResonatorResponse(resonatorName=resonator_name)


def update_resonator(db: Session, user_resonator_id: int, data: UpdateResonatorRequest) -> None:
    user_resonator = user_resonator_repository.find_by_id_for_update(db, user_resonator_id)
    if user_resonator is None:
        raise CustomException(ErrorCode.RESONATOR_NOT_FOUND)

    node_map = {f"{node.branchPosition.value}_{node.nodePosition.value}": node for node in data.nodes}

    # 10개 위치가 요청에 전부 없으면 여기서 거부한다 (누락 위치는 로그).
    required_keys = {
        f"{branch_position.value}_{node_position.value}"
        for branch_position in BranchPosition
        for node_position in NodePosition
    }
    missing_keys = required_keys - node_map.keys()
    if missing_keys:
        logger.warning(f"업데이트 요청에 누락된 공명 노드 위치가 있습니다. missing={sorted(missing_keys)}")
        raise CustomException(ErrorCode.VALIDATION_FAILED)

    # 노드 + 무기 재련 옵션에서 재계산 대상 StatType 수집
    required_type = {node.stat.type for node in data.nodes if node.stat is not None and node.stat.type is not None}

    refine_type = user_resonator.weapon_master.refine_type
    if refine_type is not None:
        required_type.add(refine_type)

    spec_calculation_service.re_calculate_final_stat(required_type, user_resonator, data.nodes, data.weaponRefineLevel)

    user_resonator.refine_level = data.weaponRefineLevel

    # 공명 노드 활성화 상태 변경 (완전성 검증을 이미 통과했으므로 직접 인덱싱)
    for node in user_resonator.user_resonance_nodes:
        key = f"{node.branch_position.value}_{node.node_position.value}"
        node.is_active = node_map[key].active

    # 변경된 엔티티(final_stat, refine_level, 노드 활성화)를 명시적으로 커밋한다.
    db.commit()


def _delete(db: Session, user_resonator_ids: List[int]) -> None:
    """commit/rollback 없음 — 호출자의 트랜잭션 경계에 속한다 (delete_resonator, create_resonator가 공유)."""
    user_resonator_repository.soft_delete_by_ids(db, user_resonator_ids)
    user_resonance_node_repository.soft_delete_by_user_resonator_ids(db, user_resonator_ids)
    user_echo_repository.soft_delete_by_user_resonator_ids(db, user_resonator_ids)
    user_echo_sub_repository.soft_delete_by_user_resonator_ids(db, user_resonator_ids)
    final_stat_repository.delete_by_user_resonator_ids(db, user_resonator_ids)


def delete_resonator(db: Session, user_resonator_ids: List[int]) -> None:
    _delete(db, user_resonator_ids)
    db.commit()
