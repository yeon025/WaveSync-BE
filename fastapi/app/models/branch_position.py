from enum import Enum


class BranchPosition(str, Enum):
    """공명 노드의 가지(branch) 위치. 멤버 이름은 대문자, 값(DB/API 노출값)은 소문자다.

    값 <-> 멤버 변환은 code / from_code로 한다. SAEnum 컬럼엔 values_callable=enum_values 필수.
    """

    LEFT_OUTER = "left_outer"
    LEFT_INNER = "left_inner"
    CENTER = "center"
    RIGHT_OUTER = "right_outer"
    RIGHT_INNER = "right_inner"

    @property
    def code(self) -> str:
        """API/DB 노출용 값 (예: left_outer)."""
        return self.value

    @classmethod
    def from_code(cls, code: str) -> "BranchPosition":
        """값(예: left_outer)을 멤버로 역변환."""
        return cls(code)
