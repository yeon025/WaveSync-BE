from enum import Enum


class StatType(str, Enum):
    """Spring entity.StatType 대응.

    DB 저장값은 Spring @Enumerated(EnumType.STRING)과 동일하게 enum 멤버 이름
    (예: ATTACK_PERCENT)이지만, Spring @JsonValue의 code 필드(예: attack_percent)와는
    다르다. Resonator 도메인에서 API 응답 스키마를 만들 때 code 값으로 변환하는 로직
    (예: Pydantic field_serializer)이 반드시 필요하다.
    """

    HP = "HP"
    HP_PERCENT = "HP_PERCENT"

    ATTACK = "ATTACK"
    ATTACK_PERCENT = "ATTACK_PERCENT"

    DEFENSE = "DEFENSE"
    DEFENSE_PERCENT = "DEFENSE_PERCENT"

    CRITICAL_RATE = "CRITICAL_RATE"
    CRITICAL_DAMAGE = "CRITICAL_DAMAGE"

    ENERGY_REGEN = "ENERGY_REGEN"

    FUSION_DAMAGE_BONUS = "FUSION_DAMAGE_BONUS"
    GLACIO_DAMAGE_BONUS = "GLACIO_DAMAGE_BONUS"
    AERO_DAMAGE_BONUS = "AERO_DAMAGE_BONUS"
    CONDUCTO_DAMAGE_BONUS = "CONDUCTO_DAMAGE_BONUS"
    SPECTRA_DAMAGE_BONUS = "SPECTRA_DAMAGE_BONUS"
    HAVOC_DAMAGE_BONUS = "HAVOC_DAMAGE_BONUS"

    BASIC_ATTACK_DAMAGE_BONUS = "BASIC_ATTACK_DAMAGE_BONUS"
    HEAVY_ATTACK_DAMAGE_BONUS = "HEAVY_ATTACK_DAMAGE_BONUS"
    RESONANCE_SKILL_DAMAGE_BONUS = "RESONANCE_SKILL_DAMAGE_BONUS"
    RESONANCE_LIBERATION_DAMAGE_BONUS = "RESONANCE_LIBERATION_DAMAGE_BONUS"
    HEALING_BONUS = "HEALING_BONUS"

    ALL_ATTRIBUTE_DAMAGE_BONUS = "ALL_ATTRIBUTE_DAMAGE_BONUS"
    BASIC_AND_HEAVY_ATTACK_DAMAGE_BONUS = "BASIC_AND_HEAVY_ATTACK_DAMAGE_BONUS"

    @property
    def code(self) -> str:
        """Spring @JsonValue의 code 필드 대응 (예: ATTACK_PERCENT -> attack_percent)."""
        return self.value.lower()

    @classmethod
    def from_code(cls, code: str) -> "StatType":
        """code 문자열(예: attack_percent)을 멤버로 역변환. 요청 바디 파싱 등 입력 경로에서 사용."""
        return cls[code.upper()]
