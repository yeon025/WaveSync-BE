package io.github.wavesync.dto.common;
import java.math.BigDecimal;
import io.github.wavesync.entity.FinalStat;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;



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

        return new ResonatorStatDto(
                finalStat.getHp(),
                finalStat.getAttack(),
                finalStat.getDefense(),
                finalStat.getEnergyRegen(),
                finalStat.getCriticalRate(),
                finalStat.getCriticalDamage(),
                finalStat.getResonanceSkillDamageBonus(),
                finalStat.getBasicAttackDamageBonus(),
                finalStat.getHeavyAttackDamageBonus(),
                finalStat.getResonanceLiberationDamageBonus(),
                finalStat.getGlacioDamageBonus(),
                finalStat.getFusionDamageBonus(),
                finalStat.getConductoDamageBonus(),
                finalStat.getAeroDamageBonus(),
                finalStat.getSpectraDamageBonus(),
                finalStat.getHavocDamageBonus(),
                finalStat.getHealingBonus()
        );
    }
}
