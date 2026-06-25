package io.github.wavesync.entity;
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.util.List;

@Entity
@Table(name = "user_echoes")
@Getter
@Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class UserEcho {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(name = "main_type", nullable = false, length = 50)
    private StatType mainType;

    @Column(name = "main_value", nullable = false, precision = 5, scale = 2)
    private BigDecimal mainValue;

    @Enumerated(EnumType.STRING)
    @Column(name = "secondary_type", nullable = false, length = 50)
    private StatType secondaryType;

    @Column(name = "secondary_value", nullable = false)
    private Integer secondaryValue;

    @Builder.Default
    @Column(name = "is_deleted", nullable = false)
    private Boolean isDeleted = false;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_resonator_id", nullable = false)
    private UserResonator userResonator;

    @OneToMany(mappedBy = "userEcho")
    private List<UserEchoSub> userEchoSubs;
}
