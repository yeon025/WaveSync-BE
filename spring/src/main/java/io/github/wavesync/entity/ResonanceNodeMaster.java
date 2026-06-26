package io.github.wavesync.entity;
import io.github.wavesync.dto.common.StatDto;
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;



@Entity
@Table(name = "resonance_node_master")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class ResonanceNodeMaster {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(name = "outer_node_type", nullable = false, length = 50)
    private StatType outerNodeType;

    @Column(name = "outer_top_node_value", nullable = false, precision = 5, scale = 1)
    private BigDecimal outerTopNodeValue;

    @Column(name = "outer_middle_node_value", nullable = false, precision = 5, scale = 1)
    private BigDecimal outerMiddleNodeValue;

    @Enumerated(EnumType.STRING)
    @Column(name = "inner_node_type", nullable = false, length = 50)
    private StatType innerNodeType;

    @Column(name = "inner_top_node_value", nullable = false, precision = 5, scale = 1)
    private BigDecimal innerTopNodeValue;

    @Column(name = "inner_middle_node_value", nullable = false, precision = 5, scale = 1)
    private BigDecimal innerMiddleNodeValue;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "resonator_master_id", nullable = false)
    private ResonatorMaster resonatorMaster;


    public StatDto getStat(BranchPosition branchPosition, NodePosition nodePosition) {
        return switch (branchPosition) {
            case LEFT_OUTER, RIGHT_OUTER ->
                    switch (nodePosition) {
                        case TOP -> new StatDto(outerNodeType, outerTopNodeValue);
                        case MIDDLE -> new StatDto(outerNodeType, outerMiddleNodeValue);
                    };

            case LEFT_INNER, RIGHT_INNER ->
                    switch (nodePosition) {
                        case TOP -> new StatDto(innerNodeType, innerTopNodeValue);
                        case MIDDLE -> new StatDto(innerNodeType, innerMiddleNodeValue);
                    };

            case CENTER -> null;
        };
    }
}