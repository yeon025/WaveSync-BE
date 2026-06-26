package io.github.wavesync.dto.response;
import lombok.*;



@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ResonatorSummaryResponseDto {

    private Long userResonatorId;

    private String resonatorName;

    private Integer rarity;

    private Integer releaseVersion;

    private String thumbnailImageUrl;
}
