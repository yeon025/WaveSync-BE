from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode



VALID_SECONDARY_TYPES = {
    "공격력",
    "HP",
}


def validate_secondary(echo_list):
    
    for i, echo in enumerate(echo_list, start=1):
        if echo.secondary.type in VALID_SECONDARY_TYPES:
            continue
        else:
            logger.warning(f"{i}번 에코 보조 옵션 이름이 마스터 데이터에 존재하지 않습니다. secondaryType={echo.secondary.type}")
            raise CustomException(ErrorCode.VALIDATION_FAILED)

    return 