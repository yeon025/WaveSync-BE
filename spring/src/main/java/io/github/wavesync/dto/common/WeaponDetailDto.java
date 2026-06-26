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

        return WeaponDetailDto.builder()
                .name(weapon.getName())
                .attackValue(weapon.getAttackValue())
                .main(new StatDto(weapon.getMainType(), weapon.getMainValue()))
                .refineLevel(userResonator.getRefineLevel())
                .imageUrl(weapon.getImage())
                .build();
    }
}
