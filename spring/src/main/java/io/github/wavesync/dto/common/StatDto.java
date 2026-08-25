// MIGRATED to fastapi/app/schemas/common.py
package io.github.wavesync.dto.common;
import io.github.wavesync.entity.StatType;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;




@Getter
@NoArgsConstructor
@AllArgsConstructor
public class StatDto {

    private StatType type;

    private BigDecimal value;
}
