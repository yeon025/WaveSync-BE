from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config.logger import logger
from app.profile_extraction.profile_extraction_service import extract_info
from app.resonator import extract_profile_validation_service, spec_calculation_service
from app.resonator.echo_score import echo_score_service
from app.resonator.schemas import CreateResonatorResponse
from app.resonator.user_resonator import user_resonator_repository
from app.resonator.user_resonator_factory import build_user_resonator
from app.storage.object_storage_factory import get_object_storage_service


def create_resonator(db: Session, resonator_profile: UploadFile) -> CreateResonatorResponse:
    storage = get_object_storage_service()
    profile_url = storage.upload(storage.profile_bucket, resonator_profile)
    logger.debug(f"{profile_url} 저장을 완료했습니다.")

    logger.info("이미지 추출을 시작합니다.")
    extracted = extract_info(profile_url)
    logger.info("이미지 추출이 완료되었습니다.")

    resonator_master, weapon_master = extract_profile_validation_service.validate(db, extracted)
    logger.debug("추출된 데이터로 데이터베이스 조회를 완료했습니다.")

    # 같은 공명자를 다시 등록하면 기존 데이터를 대체한다.
    target_ids = user_resonator_repository.find_ids_by_resonator_name(db, extracted.resonatorName)
    if target_ids:
        logger.debug(f"조회한 id: {target_ids}")
        user_resonator_repository.soft_delete_by_ids(db, target_ids)
        logger.debug("동일한 공명자 정보를 삭제했습니다.")

    user_resonator, nodes = build_user_resonator(resonator_master, weapon_master, extracted)

    user_resonator.final_stat = spec_calculation_service.calculate_final_stat(user_resonator, nodes)

    # 자식을 모두 연결한 뒤 저장해야 cascade로 함께 INSERT된다.
    user_resonator_repository.save(db, user_resonator)
    logger.debug("공명자 정보를 데이터베이스에 저장했습니다.")

    # autoflush=False라 flush해야 점수 계산의 재조회에 에코가 잡힌다.
    db.flush()
    echo_score_service.compute_and_persist_echo_scores(db, user_resonator.id)
    logger.debug("에코 점수를 계산했습니다.")

    # commit이 인스턴스를 expire시키므로 응답에 쓸 값은 미리 확보한다.
    resonator_name = resonator_master.name

    # 응답 전에 커밋해야 실패 시 클라이언트가 성공 응답을 받지 않는다.
    db.commit()
    logger.debug("공명자 등록 트랜잭션을 커밋했습니다.")

    return CreateResonatorResponse(resonatorName=resonator_name)
