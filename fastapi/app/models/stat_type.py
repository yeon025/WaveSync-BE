from enum import Enum


class StatType(str, Enum):
    """스탯 종류. 멤버 이름은 대문자, 값(DB/API 노출값)은 소문자다 (예: HP_PERCENT = "hp_percent").

    값 <-> 멤버 변환은 code / from_code로 한다. SAEnum 컬럼엔 values_callable=enum_values 필수.
    """

    HP = "hp"
    HP_PERCENT = "hp_percent"

    ATTACK = "attack"
    ATTACK_PERCENT = "attack_percent"

    DEFENSE = "defense"
    DEFENSE_PERCENT = "defense_percent"

    CRITICAL_RATE = "critical_rate"
    CRITICAL_DAMAGE = "critical_damage"

    ENERGY_REGEN = "energy_regen"

    FUSION_DAMAGE_BONUS = "fusion_damage_bonus"
    GLACIO_DAMAGE_BONUS = "glacio_damage_bonus"
    AERO_DAMAGE_BONUS = "aero_damage_bonus"
    CONDUCTO_DAMAGE_BONUS = "conducto_damage_bonus"
    SPECTRA_DAMAGE_BONUS = "spectra_damage_bonus"
    HAVOC_DAMAGE_BONUS = "havoc_damage_bonus"

    BASIC_ATTACK_DAMAGE_BONUS = "basic_attack_damage_bonus"
    HEAVY_ATTACK_DAMAGE_BONUS = "heavy_attack_damage_bonus"
    RESONANCE_SKILL_DAMAGE_BONUS = "resonance_skill_damage_bonus"
    RESONANCE_LIBERATION_DAMAGE_BONUS = "resonance_liberation_damage_bonus"
    HEALING_BONUS = "healing_bonus"

    ALL_ATTRIBUTE_DAMAGE_BONUS = "all_attribute_damage_bonus"
    BASIC_AND_HEAVY_ATTACK_DAMAGE_BONUS = "basic_and_heavy_attack_damage_bonus"

    @property
    def code(self) -> str:
        """API/DB 노출용 값 (예: hp_percent)."""
        return self.value

    @classmethod
    def from_code(cls, code: str) -> "StatType":
        """값(예: hp_percent)을 멤버로 역변환."""
        return cls(code)
