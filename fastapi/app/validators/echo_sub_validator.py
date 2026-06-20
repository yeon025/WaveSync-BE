from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode



VALID_SUB_VALUES = {
    "크리티컬": {
        6.3, 6.9, 7.5, 8.1, 8.7, 9.3, 9.9, 10.5
    },
    "크리티컬 피해": {
        12.6, 13.8, 15.0, 16.2, 17.4, 18.6, 19.8, 21.0
    },
    "공명 효율": {
        6.8, 7.6, 8.4, 9.2, 10.0, 10.8, 11.6, 12.4
    },
    "방어력": {
        8.1, 9.0, 10.0, 10.9, 11.8, 12.8, 13.8, 14.7,
        40, 50, 60, 70
    },

    # 동일한 허용값 그룹
    "일반 공격 피해 보너스": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6
    },
    "강공격 피해 보너스": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6
    },
    "공명 스킬 피해 보너스": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6
    },
    "공명 해방 피해 보너스": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6
    },
    "공격력": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6,
        30, 40, 50, 60
    },
    "HP": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6,
        320, 360, 390, 430, 470, 510, 540, 580
    }
}



def validate_sub(echo_list):
    for i, echo in enumerate(echo_list, start=1):
        for j, sub in enumerate(echo.sub, start=1):
            sub_type = sub.type
            sub_value = sub.value

            if sub_type not in VALID_SUB_VALUES:
                logger.warning(f"{i}번 에코의 {j}번 서브 속성 이름이 마스터 데이터에 존재하지 않습니다. subType={sub_type}")
                raise CustomException(ErrorCode.VALIDATION_FAILED)

            if sub_value not in VALID_SUB_VALUES[sub_type]:
                logger.warning(
                    f"{i}번 에코의 {j}번 서브 속성 값이 마스터 데이터에 존재하지 않습니다. subValue={sub_value}"
                )
                raise CustomException(ErrorCode.VALIDATION_FAILED)

    return True