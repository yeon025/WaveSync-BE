from enum import Enum


class EchoGrade(str, Enum):
    """다른 enum과 달리 값도 대문자다 (API에 표시 라벨 그대로 노출)."""

    SS = "SS"
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
