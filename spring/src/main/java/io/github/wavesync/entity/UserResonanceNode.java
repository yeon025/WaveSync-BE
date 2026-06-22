package io.github.wavesync.entity;
import jakarta.persistence.*;
import lombok.*;




@Entity
@Table(name = "user_resonance_nodes")
@Getter
@Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class UserResonanceNode {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(name = "branch_position", nullable = false)
    private BranchPosition branchPosition;

    @Enumerated(EnumType.STRING)
    @Column(name = "node_position", nullable = false)
    private NodePosition nodePosition;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive = false;

    @Column(name = "is_deleted", nullable = false)
    private Boolean isDeleted = false;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_resonator_id", nullable = false)
    private UserResonator userResonator;
}




