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
    @Column(name = "main_type", nullable = false, length = 20)
    private StatType mainType;

    @Column(name = "main_value", nullable = false, precision = 5, scale = 2)
    private BigDecimal mainValue;

    @Enumerated(EnumType.STRING)
    @Column(name = "refine_type", length = 20)
    private StatType refineType;

    @Column(name = "refine_1_value")
    private Integer refine1Value;

    @Column(name = "refine_2_value")
    private Integer refine2Value;

    @Column(name = "refine_3_value")
    private Integer refine3Value;

    @Column(name = "refine_4_value")
    private Integer refine4Value;

    @Column(name = "refine_5_value")
    private Integer refine5Value;

    @Column(nullable = false, length = 255)
    private String image;

    @OneToMany(mappedBy = "weaponMaster")
    private List<UserResonator> userResonators;
}