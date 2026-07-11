package io.github.wavesync.dto.common;
import io.github.wavesync.entity.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;



@Getter
@NoArgsConstructor
@AllArgsConstructor
public class WeaponDetailDto {

    private String name;

    private Integer attackValue;

    private StatDto main;

    private Integer refineLevel;

    private String imageUrl;

    public static WeaponDetailDto from(UserResonator userResonator, String weaponImage) {
        WeaponMaster weapon = userResonator.getWeaponMaster();

        return new WeaponDetailDto(
                weapon.getName(),
                weapon.getAttackValue(),
                new StatDto(weapon.getMainType(), weapon.getMainValue()),
                userResonator.getRefineLevel(),
                weaponImage
        );
    }
}
