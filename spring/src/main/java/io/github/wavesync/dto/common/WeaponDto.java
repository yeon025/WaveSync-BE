package io.github.wavesync.dto.common;
import lombok.*;



@Getter
@NoArgsConstructor
public class WeaponDto {

    private String name;

    private Integer attackValue;

    private StatDto main;

    private Integer refineLevel;

    private String imageUrl;
}
