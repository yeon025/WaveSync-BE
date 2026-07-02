package io.github.wavesync.dto.common;
import io.github.wavesync.entity.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;



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

        return new WeaponSettingDto(
                userResonator.getRefineLevel(),
                weaponMaster.getRefineType().getCode(),
                weaponMaster.getRefine1Value(),
                weaponMaster.getRefine2Value(),
                weaponMaster.getRefine3Value(),
                weaponMaster.getRefine4Value(),
                weaponMaster.getRefine5Value(),
                weaponMaster.getImage()
        );
    }
}
