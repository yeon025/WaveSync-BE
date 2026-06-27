package io.github.wavesync.dto.common;
import io.github.wavesync.entity.BranchPosition;
import io.github.wavesync.entity.NodePosition;
import io.github.wavesync.entity.ResonanceNodeMaster;
import io.github.wavesync.entity.UserResonanceNode;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;


@Builder
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ResonanceNodeSettingDto {

    private BranchPosition branchPosition;

    private NodePosition nodePosition;

    private Boolean active;

    private StatDto stat;


    public static ResonanceNodeSettingDto from(UserResonanceNode node, ResonanceNodeMaster nodeMaster) {

        return new ResonanceNodeSettingDto(
                node.getBranchPosition(),
                node.getNodePosition(),
                node.getIsActive(),
                nodeMaster.getStat(node.getBranchPosition(), node.getNodePosition())
        );
    }
}
