package io.github.wavesync.entity;
import com.fasterxml.jackson.annotation.JsonValue;
import lombok.Getter;
import lombok.RequiredArgsConstructor;


@Getter
@RequiredArgsConstructor
public enum BranchPosition {

    LEFT_OUTER("left_outer", "왼쪽 외곽"),
    LEFT_INNER("left_inner", "왼쪽 내부"),
    CENTER("center", "중앙"),
    RIGHT_OUTER("right_outer", "오른쪽 외곽"),
    RIGHT_INNER("right_inner", "오른쪽 내부");

    @JsonValue
    private final String code; // API 값
    private final String description; // UI 표시
}