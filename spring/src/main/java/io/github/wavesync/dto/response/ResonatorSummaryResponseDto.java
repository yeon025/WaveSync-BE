package io.github.wavesync.dto.response;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;


@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ResonatorSummaryResponseDto {

    private Long userResonatorId;

    private String resonatorName;

    private Integer rarity;

    private Integer releaseVersion;

    private String thumbnailImageUrl;
}
