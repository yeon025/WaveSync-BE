from enum import Enum


class NodePosition(str, Enum):
    """공명 노드의 상/중(top/middle) 위치. 멤버 이름은 대문자, 값(DB/API 노출값)은 소문자다.

    값 <-> 멤버 변환은 code / from_code로 한다. SAEnum 컬럼엔 values_callable=enum_values 필수.
    """

    TOP = "top"
    MIDDLE = "middle"

    @property
    def code(self) -> str:
        """API/DB 노출용 값 (예: top)."""
        return self.value

    @classmethod
    def from_code(cls, code: str) -> "NodePosition":
        """값(예: top)을 멤버로 역변환."""
        return cls(code)
