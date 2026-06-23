package io.github.wavesync.dto.request;
import jakarta.validation.constraints.NotBlank;
import lombok.*;



@Getter
@NoArgsConstructor
public class ExtractProfileRequestDto {

    @NotBlank
    private String imageUrl;
}
