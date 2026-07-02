package io.github.wavesync.entity;
import jakarta.persistence.*;
import lombok.*;
import java.util.ArrayList;
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

    @Column(name = "resonance_chain_level", nullable = false)
    private Integer resonanceChainLevel;

    @Column(name = "refine_level", nullable = false)
    private Integer refineLevel;

    @Builder.Default
    @Column(name = "is_deleted", nullable = false)
    private Boolean isDeleted = false;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "resonator_master_id", nullable = false)
    private ResonatorMaster resonatorMaster;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "weapon_master_id", nullable = false)
    private WeaponMaster weaponMaster;

    @OneToOne(mappedBy = "userResonator")
    private FinalStat finalStat;

    @Builder.Default
    @OneToMany(mappedBy = "userResonator")
    private List<UserResonanceNode> userResonanceNodes = new ArrayList<>();

    @Builder.Default
    @OneToMany(mappedBy = "userResonator")
    private List<UserEcho> userEchoes = new ArrayList<>();
}
