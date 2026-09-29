from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.profile_extraction.schemas import Echo, ExtractData, ExtractedStat
from app.resonator.echo_sub_stat_values import VALID_SUB_VALUES
from app.resonator.models.stat_type import StatType
from app.resonator.repositories import resonator_master_repository, weapon_master_repository


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


def _validate_sub_type(sub: ExtractedStat, echo_number: int, sub_number: int) -> StatType:
    try:
        return StatType.from_code(sub.type)
    except ValueError:
        logger.warning(
            f"{echo_number}번 에코의 {sub_number}번 서브 속성 이름이 마스터 데이터에 존재하지 않습니다. "
            f"subType={sub.type}"
        )
        raise CustomException(ErrorCode.VALIDATION_FAILED)


def _validate_sub_value(stat_type: StatType, sub: ExtractedStat, echo_number: int, sub_number: int) -> None:
    valid_values = VALID_SUB_VALUES.get(stat_type)

    # float -> Decimal은 str을 거친다 (직접 넣으면 이진 오차가 그대로 들어옴).
    sub_value = Decimal(str(sub.value))

    if valid_values is None or sub_value not in valid_values:
        logger.warning(
            f"{echo_number}번 에코의 {sub_number}번 서브 속성 값이 마스터 데이터에 존재하지 않습니다. "
            f"subValue={sub.value}"
        )
        raise CustomException(ErrorCode.VALIDATION_FAILED)
