package io.github.wavesync.dto.response;
import io.github.wavesync.dto.common.ResonanceNodeDto;
import io.github.wavesync.dto.common.WeaponSettingDto;
import lombok.*;
import java.util.List;



@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ResonatorSettingResponseDto {

    private List<ResonanceNodeDto> nodes;

    private WeaponSettingDto weapon;


    public static ResonatorSettingResponseDto from(List<ResonanceNodeDto> nodes, WeaponSettingDto weapon) {

        return new ResonatorSettingResponseDto(nodes, weapon);
    }
}
