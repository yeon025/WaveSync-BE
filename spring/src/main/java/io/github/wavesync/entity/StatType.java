package io.github.wavesync.entity;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;
import lombok.*;



@Getter
@RequiredArgsConstructor
public enum StatType {

    HP("hp", "체력"),
    HP_PERCENT("hp_percent", "체력%"),

    ATTACK("attack", "공격력"),
    ATTACK_PERCENT("attack_percent", "공격력%"),

    DEFENSE("defense", "방어력"),
    DEFENSE_PERCENT("defense_percent", "방어력%"),

    CRITICAL_RATE("critical_rate", "크리티컬"),
    CRITICAL_DAMAGE("critical_damage", "크리티컬 피해"),

    ENERGY_REGEN("energy_regen", "공명 효율"),

    FUSION_DAMAGE_BONUS("fusion_damage_bonus", "용융 피해 보너스"),
    GLACIO_DAMAGE_BONUS("glacio_damage_bonus", "응결 피해 보너스"),
    AERO_DAMAGE_BONUS("aero_damage_bonus", "기류 피해 보너스"),
    CONDUCTO_DAMAGE_BONUS("conducto_damage_bonus", "전도 피해 보너스"),
    SPECTRA_DAMAGE_BONUS("spectra_damage_bonus", "회절 피해 보너스"),
    HAVOC_DAMAGE_BONUS("havoc_damage_bonus", "인멸 피해 보너스"),

    BASIC_ATTACK_DAMAGE_BONUS("basic_attack_damage_bonus", "일반 공격 피해 보너스"),
    HEAVY_ATTACK_DAMAGE_BONUS("heavy_attack_damage_bonus", "강공격 피해 보너스"),
    RESONANCE_SKILL_DAMAGE_BONUS("resonance_skill_damage_bonus", "공명 스킬 피해 보너스"),
    RESONANCE_LIBERATION_DAMAGE_BONUS("resonance_liberation_damage_bonus", "공명 해방 피해 보너스"),
    HEALING_BONUS("healing_bonus", "치료 효과 보너스"),

    ALL_ATTRIBUTE_DAMAGE_BONUS("all_attribute_damage_bonus", "전체 속성 피해 보너스"),
    BASIC_AND_HEAVY_ATTACK_DAMAGE_BONUS("basic_and_heavy_attack_damage_bonus", "일반 공격과 강공격 피해 보너스");

    @JsonValue
    private final String code;          // API 값
    private final String description;    // UI 표시용
}