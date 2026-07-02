package io.github.wavesync.dto.response;
import io.github.wavesync.dto.common.EchoDto;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.util.List;


@Getter
@NoArgsConstructor
public class ExtractProfileResponseDto {

    private String resonatorName;

    private Integer resonanceChainLevel;

    private String weaponName;

    private List<EchoDto> echoes;
}
