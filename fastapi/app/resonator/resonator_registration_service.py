from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config.logger import logger
from app.profile_extraction.profile_extraction_service import extract_info
from app.resonator import extract_profile_validation_service, spec_calculation_service
from app.resonator.schemas import CreateResonatorResponse
from app.resonator.user_resonator import user_resonator_repository
from app.resonator.user_resonator_factory import build_user_resonator
from app.storage import storage_validator


def create_resonator(db: Session, user_id: int, resonator_profile: UploadFile) -> CreateResonatorResponse:
    image_content = storage_validator.validate_image(resonator_profile)
    logger.debug("프로필 이미지 검증을 완료했습니다.")

    logger.info("이미지 추출을 시작합니다.")
    extracted = extract_info(image_content)
    logger.info("이미지 추출이 완료되었습니다.")

    resonator_master, weapon_master = extract_profile_validation_service.validate(db, extracted)
    logger.debug("추출된 데이터로 데이터베이스 조회를 완료했습니다.")

    # user_id로 스코프해야 한다 — 전역으로 찾으면 다른 사용자가 같은 캐릭터를 올렸을 때
    # 그 사용자의 데이터를 지우게 된다.
    target_ids = user_resonator_repository.find_ids_by_resonator_name(db, extracted.resonatorName, user_id)
    if target_ids:
        logger.debug(f"조회한 id: {target_ids}")
        user_resonator_repository.soft_delete_by_ids(db, target_ids, user_id)
        logger.debug("동일한 공명자 정보를 삭제했습니다.")

    user_resonator, nodes = build_user_resonator(resonator_master, weapon_master, extracted)
    user_resonator.user_id = user_id

    user_resonator.final_stat = spec_calculation_service.calculate_final_stat(user_resonator, nodes)

    user_resonator_repository.save(db, user_resonator)
    logger.debug("공명자 정보를 데이터베이스에 저장했습니다.")

    resonator_name = resonator_master.name

    db.commit()
    logger.debug("공명자 등록 트랜잭션을 커밋했습니다.")

    return CreateResonatorResponse(resonatorName=resonator_name)
