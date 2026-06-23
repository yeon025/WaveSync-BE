package io.github.wavesync.dto.response;
import io.github.wavesync.dto.common.EchoDto;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.*;



@Getter
@NoArgsConstructor
public class ExtractProfileResponseDto {

    private String resonatorName;

    private Integer resonanceChainLevel;

    private String weaponName;

    private EchoDto echoes;
}
