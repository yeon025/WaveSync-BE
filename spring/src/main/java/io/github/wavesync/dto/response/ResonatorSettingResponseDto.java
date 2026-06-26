package io.github.wavesync.dto.response;
import io.github.wavesync.dto.common.ResonanceNodeSettingDto;
import io.github.wavesync.dto.common.WeaponSettingDto;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.util.List;


@Builder
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ResonatorSettingResponseDto {

    private List<ResonanceNodeSettingDto> nodes;

    private WeaponSettingDto weapon;


    public static ResonatorSettingResponseDto from(List<ResonanceNodeSettingDto> nodes, WeaponSettingDto weapon) {
        return ResonatorSettingResponseDto.builder()
                .nodes(nodes)
                .weapon(weapon)
                .build();
    }
}
