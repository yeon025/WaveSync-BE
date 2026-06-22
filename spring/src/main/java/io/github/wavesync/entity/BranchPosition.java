package io.github.wavesync.entity;
import lombok.*;


@Getter
@RequiredArgsConstructor
public enum BranchPosition {
    TOP("top", "상단"),
    MIDDLE("middle", "중단");

    private final String code; // API, DB 값
    private final String description; // UI 표시
}