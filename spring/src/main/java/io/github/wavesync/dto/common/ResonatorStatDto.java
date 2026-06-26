package io.github.wavesync.dto.common;
import java.math.BigDecimal;

import io.github.wavesync.entity.FinalStat;
import lombok.*;


@Builder
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ResonatorStatDto {

    private Integer hp;

    private Integer attack;

    private Integer defense;

    private BigDecimal energyRegen;

    private BigDecimal criticalRate;

    private BigDecimal criticalDamage;

    private BigDecimal resonanceSkillDamageBonus;

    private BigDecimal basicAttackDamageBonus;

    private BigDecimal heavyAttackDamageBonus;

    private BigDecimal resonanceLiberationDamageBonus;

    private BigDecimal glacioDamageBonus;

    private BigDecimal fusionDamageBonus;

    private BigDecimal conductoDamageBonus;

    private BigDecimal aeroDamageBonus;

    private BigDecimal spectraDamageBonus;

    private BigDecimal havocDamageBonus;

    private BigDecimal healingBonus;


    public static ResonatorStatDto from(FinalStat finalStat) {
        return ResonatorStatDto.builder()
                .hp(finalStat.getHp())
                .attack(finalStat.getAttack())
                .defense(finalStat.getDefense())
                .energyRegen(finalStat.getEnergyRegen())
                .criticalRate(finalStat.getCriticalRate())
                .criticalDamage(finalStat.getCriticalDamage())
                .resonanceSkillDamageBonus(finalStat.getResonanceSkillDamageBonus())
                .basicAttackDamageBonus(finalStat.getBasicAttackDamageBonus())
                .heavyAttackDamageBonus(finalStat.getHeavyAttackDamageBonus())
                .resonanceLiberationDamageBonus(finalStat.getResonanceLiberationDamageBonus())
                .glacioDamageBonus(finalStat.getGlacioDamageBonus())
                .fusionDamageBonus(finalStat.getFusionDamageBonus())
                .conductoDamageBonus(finalStat.getConductoDamageBonus())
                .aeroDamageBonus(finalStat.getAeroDamageBonus())
                .spectraDamageBonus(finalStat.getSpectraDamageBonus())
                .havocDamageBonus(finalStat.getHavocDamageBonus())
                .healingBonus(finalStat.getHealingBonus())
                .build();
    }
}
