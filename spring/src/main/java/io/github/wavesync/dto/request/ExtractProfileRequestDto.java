package io.github.wavesync.dto.request;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.*;



@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ExtractProfileRequestDto {

    @NotBlank
    @JsonProperty("imageUrl")
    private String imageUrl;
}
