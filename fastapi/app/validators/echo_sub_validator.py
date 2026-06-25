from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode



VALID_SUB_VALUES = {
    "critical_rate": {
        6.3, 6.9, 7.5, 8.1, 8.7, 9.3, 9.9, 10.5
    },
    "critical_damage": {
        12.6, 13.8, 15.0, 16.2, 17.4, 18.6, 19.8, 21.0
    },
    "energy_regen": {
        6.8, 7.6, 8.4, 9.2, 10.0, 10.8, 11.6, 12.4
    },

    "defense_percent": {
        8.1, 9.0, 10.0, 10.9, 11.8, 12.8, 13.8, 14.7
    },
    "defense": {
        40, 50, 60, 70
    },

    "attack_percent": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6
    },
    "attack": {
        30, 40, 50, 60
    },

    "hp_percent": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6
    },
    "hp": {
        320, 360, 390, 430, 470, 510, 540, 580
    },

    # 동일한 허용값 그룹
    "basic_attack_damage_bonus": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6
    },
    "heavy_attack_damage_bonus": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6
    },
    "resonance_skill_damage_bonus": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6
    },
    "resonance_liberation_damage_bonus": {
        6.4, 7.1, 7.9, 8.6, 9.4, 10.1, 10.9, 11.6
    }
}



def validate_sub(echo_list):
    for i, echo in enumerate(echo_list, start=1):
        for j, sub in enumerate(echo.subs, start=1):

            sub_type = sub.type
            sub_value = sub.value

            # 타입 검증
            if sub_type not in VALID_SUB_VALUES:
                logger.warning(
                    f"{i}번 에코의 {j}번 서브 속성 이름이 마스터 데이터에 존재하지 않습니다. subType={sub_type}"
                )
                raise CustomException(ErrorCode.VALIDATION_FAILED)

            # 값 검증
            if sub_value not in VALID_SUB_VALUES[sub_type]:
                logger.warning(
                    f"{i}번 에코의 {j}번 서브 속성 값이 마스터 데이터에 존재하지 않습니다. subValue={sub_value}"
                )
                raise CustomException(ErrorCode.VALIDATION_FAILED)