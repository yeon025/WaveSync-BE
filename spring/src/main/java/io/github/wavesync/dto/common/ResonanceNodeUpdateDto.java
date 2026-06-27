package io.github.wavesync.dto.common;
import io.github.wavesync.entity.BranchPosition;
import io.github.wavesync.entity.NodePosition;
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
}
