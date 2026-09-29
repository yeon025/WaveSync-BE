from enum import Enum


class DamageType(str, Enum):
    """SAEnum 컬럼이 아니라 resonator_damage_master.relevant_damage_types(JSON 배열)의 원소 값이다."""

    BASIC_ATTACK = "basic_attack"
    HEAVY_ATTACK = "heavy_attack"
    RESONANCE_SKILL = "resonance_skill"
    RESONANCE_LIBERATION = "resonance_liberation"
