from decimal import Decimal
from typing import Set

from app.resonator.models.stat_type import StatType

# 에코 서브옵션이 가질 수 있는 유효 수치 집합 (명조 게임 밸런스 데이터).
# OCR 검증(profile_extraction/validation)의 오독 판별 기준이자,
# echo_score_service의 정규화 분모(_SUB_V_MAX)로도 쓰인다 — 소유는 resonator/echo 도메인.


def _decimals(*values: str) -> Set[Decimal]:
    return {Decimal(v) for v in values}


_DAMAGE_BONUS_VALUES = _decimals("6.4", "7.1", "7.9", "8.6", "9.4", "10.1", "10.9", "11.6")

VALID_SUB_VALUES = {
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
