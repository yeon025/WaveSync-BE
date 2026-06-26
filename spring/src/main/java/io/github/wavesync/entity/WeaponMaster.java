package io.github.wavesync.entity;
import jakarta.persistence.*;
import java.util.List;
import lombok.*;
import java.math.BigDecimal;




@Entity
@Table(name = "weapon_master")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class WeaponMaster {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 50, unique = true)
    private String name;

    @Column(name = "attack_value", nullable = false)
    private Integer attackValue;

    @Enumerated(EnumType.STRING)
    @Column(name = "main_type", nullable = false, length = 50)
    private StatType mainType;

    @Column(name = "main_value", nullable = false, precision = 5, scale = 1)
    private BigDecimal mainValue;

    @Enumerated(EnumType.STRING)
    @Column(name = "refine_type", length = 70)
    private StatType refineType;

    @Column(name = "refine_1_value", precision = 5, scale = 1)
    private BigDecimal refine1Value;

    @Column(name = "refine_2_value", precision = 5, scale = 1)
    private BigDecimal refine2Value;

    @Column(name = "refine_3_value", precision = 5, scale = 1)
    private BigDecimal refine3Value;

    @Column(name = "refine_4_value", precision = 5, scale = 1)
    private BigDecimal refine4Value;

    @Column(name = "refine_5_value", precision = 5, scale = 1)
    private BigDecimal refine5Value;

    @Column(nullable = false, length = 255)
    private String image;

    @OneToMany(mappedBy = "weaponMaster")
    private List<UserResonator> userResonators;


    public BigDecimal getRefineValue(int refineLevel) {
        return switch (refineLevel) {
            case 1 -> refine1Value;
            case 2 -> refine2Value;
            case 3 -> refine3Value;
            case 4 -> refine4Value;
            case 5 -> refine5Value;
            default -> throw new IllegalArgumentException("Invalid refine level: " + refineLevel);
        };
    }
}