from enum import Enum


class EchoGrade(str, Enum):
    """에코 서브속성 점수 등급. 다른 enum과 달리 값도 대문자다 (API에 표시 라벨 그대로 노출).

    SAEnum 컬럼엔 values_callable=enum_values 필수.
    """

    SS = "SS"
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
