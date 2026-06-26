package io.github.wavesync.dto.request;
import io.github.wavesync.dto.common.ResonanceNodeUpdateDto;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.util.List;
import lombok.*;




@Getter
@NoArgsConstructor
public class UpdateResonatorRequestDto {

    @Min(1)
    @Max(5)
    @NotNull
    private Integer weaponRefineLevel;

    @Valid
    @NotEmpty
    private List<@NotNull ResonanceNodeUpdateDto> nodes;
}
