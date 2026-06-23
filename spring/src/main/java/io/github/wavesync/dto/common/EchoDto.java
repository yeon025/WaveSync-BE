package io.github.wavesync.dto.common;
import java.util.List;
import lombok.*;




@Getter
@NoArgsConstructor
public class EchoDto {

    private StatDto main;

    private StatDto secondary;

    private List<StatDto> subs;
}
