package io.github.wavesync.dto.response;
import jakarta.validation.constraints.NotBlank;
import lombok.*;



@Getter
@NoArgsConstructor
public class CreateResonatorResponseDto {

    private String resonatorName;
}
