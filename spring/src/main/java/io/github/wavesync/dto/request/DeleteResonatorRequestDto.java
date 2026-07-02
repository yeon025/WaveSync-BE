package io.github.wavesync.dto.request;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.util.List;




@Getter
@NoArgsConstructor
public class DeleteResonatorRequestDto {

    @NotEmpty
    private List<@NotNull @Positive Long> userResonatorIds;
}
