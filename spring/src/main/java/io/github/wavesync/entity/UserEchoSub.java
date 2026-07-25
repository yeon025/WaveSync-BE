package io.github.wavesync.entity;
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;



@Entity
@Table(name = "user_echo_sub")
@Getter
@Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class UserEchoSub {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "user_echo_sub_seq")
    @SequenceGenerator(
            name = "user_echo_sub_seq",
            sequenceName = "user_echo_sub_seq",
            allocationSize = 50
    )
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(name = "type", nullable = false, length = 50)
    private StatType type;

    @Column(name = "value", nullable = false, precision = 7, scale = 1)
    private BigDecimal value;

    @Builder.Default
    @Column(name = "is_deleted", nullable = false)
    private Boolean isDeleted = false;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_echo_id", nullable = false)
    private UserEcho userEcho;
}
