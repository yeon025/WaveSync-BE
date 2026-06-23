package io.github.wavesync.dto.common;
import io.github.wavesync.entity.StatType;
import java.math.BigDecimal;
import lombok.*;



@Getter
@NoArgsConstructor
public class StatDto {

    private StatType type;

    private BigDecimal value;
}
