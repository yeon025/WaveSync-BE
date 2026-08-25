from decimal import Decimal
from typing import List, Set
from sqlalchemy.orm import Session
from app.models.stat_type import StatType
from app.repositories import resonator_master_repository, weapon_master_repository
from app.schemas.response import ExtractData, Echo, Stat
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.config.logger import logger


# Spring service.ExtractProfileValidationService 대응.
#
# Spring의 StatDto{type: StatType, value: BigDecimal}는 Jackson이 JSON 역직렬화 단계에서
# 자동으로 만들어주지만, FastAPI의 ExtractData/Echo/Stat(이미 존재하는 OCR 결과 스키마)는
# type이 소문자 code 문자열(예: "hp_percent"), value가 float라 여기서 직접 변환한다.
# StatType.from_code() 실패(KeyError)는 Spring에선 Jackson 역직렬화 단계에서 걸러져
# 이 서비스까지 도달할 수 없던 경우지만, 여기선 sub.getType() == null과 동일하게 취급한다.


def _decimals(*values: str) -> Set[Decimal]:
    return {Decimal(v) for v in values}


_DAMAGE_BONUS_VALUES = _decimals("6.4", "7.1", "7.9", "8.6", "9.4", "10.1", "10.9", "11.6")

# Spring ExtractProfileValidationService.createValidSubValues() 1:1 포팅 (13개 키)
_VALID_SUB_VALUES = {
    StatType.CRITICAL_RATE: _decimals("6.3", "6.9", "7.5", "8.1", "8.7", "9.3", "9.9", "10.5"),
    StatType.CRITICAL_DAMAGE: _decimals("12.6", "13.8", "15.0", "16.2", "17.4", "18.6", "19.8", "21.0"),
    StatType.ENERGY_REGEN: _decimals("6.8", "7.6", "8.4", "9.2", "10.0", "10.8", "11.6", "12.4"),
    StatType.DEFENSE_PERCENT: _decimals("8.1", "9.0", "10.0", "10.9", "11.8", "12.8", "13.8", "14.7"),
    StatType.DEFENSE: _decimals("40", "50", "60", "70"),
    StatType.ATTACK_PERCENT: _decimals("6.4", "7.1", "7.9", "8.6", "9.4", "10.1", "10.9", "11.6"),
    StatType.ATTACK: _decimals("30", "40", "50", "60"),
    StatType.HP_PERCENT: _decimals("6.4", "7.1", "7.9", "8.6", "9.4", "10.1", "10.9", "11.6"),
    StatType.HP: _decimals("320", "360", "390", "430", "470", "510", "540", "580"),
    StatType.BASIC_ATTACK_DAMAGE_BONUS: _DAMAGE_BONUS_VALUES,
    StatType.HEAVY_ATTACK_DAMAGE_BONUS: _DAMAGE_BONUS_VALUES,
    StatType.RESONANCE_SKILL_DAMAGE_BONUS: _DAMAGE_BONUS_VALUES,
    StatType.RESONANCE_LIBERATION_DAMAGE_BONUS: _DAMAGE_BONUS_VALUES,
}


def validate(db: Session, dto: ExtractData) -> str:
    _validate_resonator(db, dto.resonatorName)

    weapon_name = _validate_weapon(db, dto.weaponName)

    _validate_subs(dto.echoes)

    return weapon_name


def _validate_resonator(db: Session, resonator_name: str) -> None:
    if not resonator_master_repository.exists_by_name(db, resonator_name):
        logger.warning(f"공명자 이름이 마스터 데이터에 존재하지 않습니다. resonatorName={resonator_name}")
        raise CustomException(ErrorCode.VALIDATION_FAILED)


def _validate_weapon(db: Session, extracted_name: str) -> str:
    weapon = weapon_master_repository.find_by_name_without_spaces(db, extracted_name)

    if weapon is None:
        logger.warning(f"무기 이름이 마스터 데이터에 존재하지 않습니다. weaponName={extracted_name}")
        raise CustomException(ErrorCode.VALIDATION_FAILED)

    return weapon.name


def _validate_subs(echoes: List[Echo]) -> None:
    for i, echo in enumerate(echoes):
        for j, sub in enumerate(echo.subs):
            stat_type = _validate_sub_type(sub, i + 1, j + 1)
            _validate_sub_value(stat_type, sub, i + 1, j + 1)


def _validate_sub_type(sub: Stat, echo_number: int, sub_number: int) -> StatType:
    try:
        return StatType.from_code(sub.type)
    except KeyError:
        logger.warning(
            f"{echo_number}번 에코의 {sub_number}번 서브 속성 이름이 마스터 데이터에 존재하지 않습니다. "
            f"subType={sub.type}"
        )
        raise CustomException(ErrorCode.VALIDATION_FAILED)


def _validate_sub_value(stat_type: StatType, sub: Stat, echo_number: int, sub_number: int) -> None:
    valid_values = _VALID_SUB_VALUES.get(stat_type)

    # float -> Decimal은 반드시 str을 거친다. Decimal(sub.value)는 IEEE754 이진 오차가
    # 그대로 들어와 Decimal('6.29999999999999982236...') 같은 값이 되어버린다.
    sub_value = Decimal(str(sub.value))

    if valid_values is None or sub_value not in valid_values:
        logger.warning(
            f"{echo_number}번 에코의 {sub_number}번 서브 속성 값이 마스터 데이터에 존재하지 않습니다. "
            f"subValue={sub.value}"
        )
        raise CustomException(ErrorCode.VALIDATION_FAILED)
