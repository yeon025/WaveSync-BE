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
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(name = "type", nullable = false, length = 20)
    private StatType type;

    @Column(name = "value", nullable = false, precision = 7, scale = 2)
    private BigDecimal value;

    @Column(name = "is_deleted", nullable = false)
    private Boolean isDeleted = false;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_echo_id", nullable = false)
    private UserEcho userEcho;
}