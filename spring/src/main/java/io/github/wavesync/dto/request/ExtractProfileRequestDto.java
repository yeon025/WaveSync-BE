package io.github.wavesync.dto.request;
import jakarta.validation.constraints.*;
import lombok.*;



@Getter
@NoArgsConstructor
public class ExtractProfileRequestDto {
    @NotBlank
    private String imageUrl;
}
