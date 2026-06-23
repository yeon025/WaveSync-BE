package io.github.wavesync.dto.response;
import io.github.wavesync.dto.common.*;
import java.util.List;
import lombok.*;



@Getter
@NoArgsConstructor
public class ResonatorDetailResponseDto {

    private Long userResonatorId;

    private String resonatorName;

    private String resonatorImageUrl;

    private Integer resonanceChainLevel;

    private List<ResonanceNodeDto> nodes;

    private WeaponDto weapon;

    private ResonatorStatDto stat;
}
