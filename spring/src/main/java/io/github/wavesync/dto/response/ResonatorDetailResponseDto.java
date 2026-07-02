package io.github.wavesync.dto.response;
import io.github.wavesync.dto.common.*;
import io.github.wavesync.entity.UserResonator;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;


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


    public static ResonatorDetailResponseDto from(UserResonator userResonator, WeaponDetailDto weapon, ResonatorStatDto stat) {

        return new ResonatorDetailResponseDto(
                userResonator.getId(),
                userResonator.getResonatorMaster().getName(),
                userResonator.getResonatorMaster().getElement().getCode(),
                userResonator.getResonatorMaster().getStandingImage(),
                userResonator.getResonanceChainLevel(),
                weapon,
                stat
        );
    }
}
