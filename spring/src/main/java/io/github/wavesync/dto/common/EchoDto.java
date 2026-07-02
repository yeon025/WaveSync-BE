package io.github.wavesync.dto.common;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.util.List;




@Getter
@NoArgsConstructor
public class EchoDto {

    private StatDto main;

    private StatDto secondary;

    private List<StatDto> subs;
}
