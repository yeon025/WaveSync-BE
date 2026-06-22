package io.github.wavesync.entity;
import lombok.*;



@Getter
@RequiredArgsConstructor
public enum Element {

    GLACIO("glacio", "응결"),
    FUSION("fusion", "용융"),
    AERO("aero", "기류"),
    CONDUCTO("conducto", "전도"),
    SPECTRO("spectro", "회절"),
    HAVOC("havoc", "인멸");

    private final String code;        // API / DB 값
    private final String description; // UI 표시용
}
