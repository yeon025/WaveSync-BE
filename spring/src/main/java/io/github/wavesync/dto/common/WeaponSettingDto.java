package io.github.wavesync.dto.common;

import io.github.wavesync.entity.UserResonator;
import io.github.wavesync.entity.WeaponMaster;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;


@Builder
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class WeaponSettingDto {

    private Integer refineLevel;

    private String refineType;

    private BigDecimal refine1Value;

    private BigDecimal refine2Value;

    private BigDecimal refine3Value;

    private BigDecimal refine4Value;

    private BigDecimal refine5Value;

    private String imageUrl;

    public static WeaponSettingDto from(UserResonator userResonator) {
        WeaponMaster weaponMaster = userResonator.getWeaponMaster();

        return WeaponSettingDto.builder()
                .refineLevel(userResonator.getRefineLevel())
                .refineType(weaponMaster.getRefineType().getCode())
                .refine1Value(weaponMaster.getRefine1Value())
                .refine2Value(weaponMaster.getRefine2Value())
                .refine3Value(weaponMaster.getRefine3Value())
                .refine4Value(weaponMaster.getRefine4Value())
                .refine5Value(weaponMaster.getRefine5Value())
                .imageUrl(weaponMaster.getImage())
                .build();
    }
}
