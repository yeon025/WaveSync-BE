package io.github.wavesync.entity;
import lombok.*;


@Getter
@RequiredArgsConstructor
public enum NodePosition {

    TOP("top", "상단"),
    MIDDLE("middle", "중단");

    private final String code; // API 값
    private final String description; // UI 표시
}