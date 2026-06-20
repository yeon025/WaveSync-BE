from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode



VALID_MAIN_TYPES = {
    "공격력",
    "HP",
    "방어력",
    "용융 피해 보너스",
    "응결 피해 보너스",
    "전도 피해 보너스",
    "기류 피해 보너스",
    "회절 피해 보너스",
    "인멸 피해 보너스",
    "공명 효율",
    "크리티컬",
    "크리티컬 피해",
    "치료 효과 보너스",
}


def validate_main(echo_list):
    
    for i, echo in enumerate(echo_list, start=1):
        if echo.main.type in VALID_MAIN_TYPES:
            continue
        else:
            logger.warning(f"{i}번 에코 주 옵션 이름이 마스터 데이터에 존재하지 않습니다. mainType={echo.main.type}")
            raise CustomException(ErrorCode.VALIDATION_FAILED)
    return 