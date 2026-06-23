package io.github.wavesync.entity;
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

@Entity
@Table(name = "final_stats")
@Getter
@Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class FinalStat {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Integer hp;

    @Column(nullable = false)
    private Integer attack;

    @Column(nullable = false)
    private Integer defense;

    @Column(name = "energy_regen", nullable = false, precision = 5, scale = 2)
    private BigDecimal energyRegen;

    @Column(name = "critical_rate",nullable = false, precision = 5, scale = 2)
    private BigDecimal criticalRate;

    @Column(name = "critical_damage", nullable = false, precision = 5, scale = 2)
    private BigDecimal criticalDamage;

    @Column(name = "resonance_skill_damage_bonus", nullable = false, precision = 5, scale = 2)
    private BigDecimal resonanceSkillDamageBonus;

    @Column(name = "basic_attack_damage_bonus", nullable = false, precision = 5, scale = 2)
    private BigDecimal basicAttackDamageBonus;

    @Column(name = "heavy_attack_damage_bonus", nullable = false, precision = 5, scale = 2)
    private BigDecimal heavyAttackDamageBonus;

    @Column(name = "resonance_liberation_damage_bonus", nullable = false, precision = 5, scale = 2)
    private BigDecimal resonanceLiberationDamageBonus;

    @Column(name = "glacio_damage_bonus", nullable = false, precision = 5, scale = 2)
    private BigDecimal glacioDamageBonus;

    @Column(name = "fusion_damage_bonus", nullable = false, precision = 5, scale = 2)
    private BigDecimal fusionDamageBonus;

    @Column(name = "conducto_damage_bonus", nullable = false, precision = 5, scale = 2)
    private BigDecimal conductoDamageBonus;

    @Column(name = "aero_damage_bonus", nullable = false, precision = 5, scale = 2)
    private BigDecimal aeroDamageBonus;

    @Column(name = "spectro_damage_bonus", nullable = false, precision = 5, scale = 2)
    private BigDecimal spectroDamageBonus;

    @Column(name = "havoc_damage_bonus", nullable = false, precision = 5, scale = 2)
    private BigDecimal havocDamageBonus;

    @Column(name = "healing_bonus", nullable = false, precision = 5, scale = 2)
    private BigDecimal healingBonus;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_resonator_id", nullable = false)
    private UserResonator userResonator;
}