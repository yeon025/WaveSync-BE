package io.github.wavesync.dto.request;
import io.github.wavesync.dto.common.ResonanceNodeDto;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.util.List;




@Getter
@NoArgsConstructor
public class UpdateResonatorRequestDto {

    @Min(1)
    @Max(5)
    @NotNull
    private Integer weaponRefineLevel;

    @Valid
    @NotEmpty
    private List<@NotNull ResonanceNodeDto> nodes;
}
