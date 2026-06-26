package io.github.wavesync.dto.response;
import io.github.wavesync.dto.common.*;
import lombok.*;


@Builder
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ResonatorDetailResponseDto {

    private Long userResonatorId;

    private String resonatorName;

    private String element;

    private String standingImageUrl;

    private Integer resonanceChainLevel;

    private WeaponDetailDto weapon;

    private ResonatorStatDto stat;
}
