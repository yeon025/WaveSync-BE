package io.github.wavesync.dto.common;

import io.github.wavesync.entity.UserResonator;
import io.github.wavesync.entity.WeaponMaster;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;


@Builder
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class WeaponSettingDto {

    private Integer refineLevel;

    private StatDto refine;

    private String imageUrl;

    public static WeaponSettingDto from(UserResonator userResonator) {
        WeaponMaster weapon = userResonator.getWeaponMaster();

        return WeaponSettingDto.builder()
                .refineLevel(userResonator.getRefineLevel())
                .refine(new StatDto(
                        weapon.getRefineType(),
                        weapon.getRefineValue(userResonator.getRefineLevel())
                ))
                .imageUrl(weapon.getImage())
                .build();
    }
}
