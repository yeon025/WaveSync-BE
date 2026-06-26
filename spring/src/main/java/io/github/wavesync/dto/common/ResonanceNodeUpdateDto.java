package io.github.wavesync.dto.common;
import io.github.wavesync.entity.BranchPosition;
import io.github.wavesync.entity.NodePosition;
import io.github.wavesync.entity.UserResonanceNode;
import jakarta.validation.constraints.*;
import lombok.*;


@Builder
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ResonanceNodeUpdateDto {
    @NotNull
    private BranchPosition branchPosition;

    @NotNull
    private NodePosition nodePosition;

    @NotNull
    private Boolean active;


    public static ResonanceNodeUpdateDto from(UserResonanceNode node) {
        return ResonanceNodeUpdateDto.builder()
                .branchPosition(node.getBranchPosition())
                .nodePosition(node.getNodePosition())
                .active(node.getIsActive())
                .build();
    }
}
