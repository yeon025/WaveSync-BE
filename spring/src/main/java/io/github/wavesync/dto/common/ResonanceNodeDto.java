package io.github.wavesync.dto.common;
import io.github.wavesync.entity.BranchPosition;
import io.github.wavesync.entity.NodePosition;
import jakarta.validation.constraints.*;
import lombok.*;



@Getter
@NoArgsConstructor
public class ResonanceNodeDto {
    @NotNull
    private BranchPosition branchPosition;

    @NotNull
    private NodePosition nodePosition;

    @NotNull
    private Boolean active;
}
