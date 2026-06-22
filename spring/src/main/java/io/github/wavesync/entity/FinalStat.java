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

    private Integer hp;
    private Integer attack;
    private Integer defense;

    @Column(precision = 5, scale = 2)
    private BigDecimal resonanceEfficiency;

    @Column(precision = 5, scale = 2)
    private BigDecimal criticalRate;

    @Column(precision = 5, scale = 2)
    private BigDecimal criticalDamage;

    @Column(precision = 5, scale = 2)
    private BigDecimal resonanceSkillDamageBonus;

    @Column(precision = 5, scale = 2)
    private BigDecimal basicAttackDamageBonus;

    @Column(precision = 5, scale = 2)
    private BigDecimal heavyAttackDamageBonus;

    @Column(precision = 5, scale = 2)
    private BigDecimal resonanceLiberationDamageBonus;

    @Column(precision = 5, scale = 2)
    private BigDecimal glacioDamageBonus;

    @Column(precision = 5, scale = 2)
    private BigDecimal fusionDamageBonus;

    @Column(precision = 5, scale = 2)
    private BigDecimal conductoDamageBonus;

    @Column(precision = 5, scale = 2)
    private BigDecimal aeroDamageBonus;

    @Column(precision = 5, scale = 2)
    private BigDecimal spectroDamageBonus;

    @Column(precision = 5, scale = 2)
    private BigDecimal havocDamageBonus;

    @Column(precision = 5, scale = 2)
    private BigDecimal healingBonus;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_resonator_id", nullable = false)
    private UserResonator userResonator;
}