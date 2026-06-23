package io.github.wavesync.dto.common;
import java.math.BigDecimal;
import lombok.*;



@Getter
@NoArgsConstructor
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

    private BigDecimal spectroDamageBonus;

    private BigDecimal havocDamageBonus;

    private BigDecimal healingBonus;
}
