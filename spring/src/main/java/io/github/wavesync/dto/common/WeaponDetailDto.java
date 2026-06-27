package io.github.wavesync.dto.common;
import io.github.wavesync.entity.UserResonator;
import io.github.wavesync.entity.WeaponMaster;
import lombok.*;


@Builder
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class WeaponDetailDto {

    private String name;

    private Integer attackValue;

    private StatDto main;

    private Integer refineLevel;

    private String imageUrl;

    public static WeaponDetailDto from(UserResonator userResonator) {
        WeaponMaster weapon = userResonator.getWeaponMaster();

        return new WeaponDetailDto(
                weapon.getName(),
                weapon.getAttackValue(),
                new StatDto(weapon.getMainType(), weapon.getMainValue()),
                userResonator.getRefineLevel(),
                weapon.getImage()
        );
    }
}
