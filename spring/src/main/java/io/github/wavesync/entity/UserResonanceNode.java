// MIGRATED to fastapi/app/models/user_resonance_node.py
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
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "user_node_seq")
    @SequenceGenerator(
            name = "user_node_seq",
            sequenceName = "user_node_seq",
            allocationSize = 50
    )
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(name = "branch_position", nullable = false, length = 20)
    private BranchPosition branchPosition;

    @Enumerated(EnumType.STRING)
    @Column(name = "node_position", nullable = false, length = 20)
    private NodePosition nodePosition;

    @Builder.Default
    @Column(name = "is_active", nullable = false)
    private Boolean isActive = true;

    @Builder.Default
    @Column(name = "is_deleted", nullable = false)
    private Boolean isDeleted = false;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_resonator_id", nullable = false)
    private UserResonator userResonator;
}




