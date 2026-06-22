package io.github.wavesync.entity;
import lombok.*;


@Getter
@RequiredArgsConstructor
public enum NodePosition {
    OUTER("outer", "외곽"),
    INNER("inner", "내부");

    private final String code; // API, DB 값
    private final String description; // UI 표시
}