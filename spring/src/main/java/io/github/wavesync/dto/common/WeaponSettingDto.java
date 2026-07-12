package io.github.wavesync.dto.common;
import io.github.wavesync.entity.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;
import java.util.Optional;


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

    public static WeaponSettingDto from(UserResonator userResonator, String weaponImage) {
        WeaponMaster weaponMaster = userResonator.getWeaponMaster();

        String refineType = Optional.ofNullable(weaponMaster.getRefineType())
                .map(StatType::getCode)
                .orElse(null);

        return new WeaponSettingDto(
                userResonator.getRefineLevel(),
                refineType,
                weaponMaster.getRefine1Value(),
                weaponMaster.getRefine2Value(),
                weaponMaster.getRefine3Value(),
                weaponMaster.getRefine4Value(),
                weaponMaster.getRefine5Value(),
                weaponImage
        );
    }
}
