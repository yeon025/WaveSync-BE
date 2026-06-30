package io.github.wavesync.dto.common;
import io.github.wavesync.entity.BranchPosition;
import io.github.wavesync.entity.NodePosition;
import io.github.wavesync.entity.ResonanceNodeMaster;
import io.github.wavesync.entity.UserResonanceNode;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;



@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ResonanceNodeDto {

    @NotNull
    private BranchPosition branchPosition;

    @NotNull
    private NodePosition nodePosition;

    @NotNull
    private Boolean active;

    private StatDto stat;


    public static ResonanceNodeDto from(UserResonanceNode node, ResonanceNodeMaster nodeMaster) {

        return new ResonanceNodeDto(
                node.getBranchPosition(),
                node.getNodePosition(),
                node.getIsActive(),
                nodeMaster.getStat(node.getBranchPosition(), node.getNodePosition())
        );
    }
}
