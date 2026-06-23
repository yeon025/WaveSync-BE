package io.github.wavesync.dto.request;
import jakarta.validation.constraints.*;
import java.util.List;
import lombok.*;



@Getter
@NoArgsConstructor
public class DeleteResonatorRequestDto {

    @NotEmpty
    private List<@NotNull @Positive Long> userResonatorIds;
}
