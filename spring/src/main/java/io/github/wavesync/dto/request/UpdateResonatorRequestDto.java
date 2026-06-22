package io.github.wavesync.dto.request;
import io.github.wavesync.dto.common.ResonanceNodeDto;
import jakarta.validation.constraints.*;
import java.util.List;
import lombok.*;




@Getter
@NoArgsConstructor
public class UpdateResonatorRequestDto {
    @Min(1)
    @Max(5)
    @NotBlank
    private Integer weaponRefineLevel;

    @NotBlank
    private List<ResonanceNodeDto> nodes;
}
