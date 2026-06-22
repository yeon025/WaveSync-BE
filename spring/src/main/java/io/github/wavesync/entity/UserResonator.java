package io.github.wavesync.entity;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;
import java.util.List;




@Entity
@Table(name = "user_resonators")
@Getter
@Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class UserResonator {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Min(0)
    @Max(6)
    @Column(name = "resonance_chain_level", nullable = false)
    private Integer resonanceChainLevel;

    @Min(1)
    @Max(5)
    @Column(name = "refine_level", nullable = false)
    private Integer refineLevel;

    @Column(name = "is_deleted", nullable = false)
    private Boolean isDeleted = false;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "resonator_master_id", nullable = false)
    private ResonatorMaster resonatorMaster;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "weapon_master_id", nullable = false)
    private WeaponMaster weaponMaster;

    @OneToMany(mappedBy = "userResonator")
    private List<UserEcho> echoes;

    @OneToOne(mappedBy = "userResonator")
    private UserResonanceNode userResonanceNode;

    @OneToOne(mappedBy = "userResonator")
    private FinalStat finalStat;
}
