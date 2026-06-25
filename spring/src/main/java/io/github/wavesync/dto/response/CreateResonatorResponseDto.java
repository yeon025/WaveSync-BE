package io.github.wavesync.dto.response;
import io.github.wavesync.entity.ResonatorMaster;
import lombok.*;



@Getter
@AllArgsConstructor
public class CreateResonatorResponseDto {

    private String resonatorName;

    public static CreateResonatorResponseDto from(ResonatorMaster resonatorMaster) {
        return new CreateResonatorResponseDto(resonatorMaster.getName());
    }
}
