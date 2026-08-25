from enum import Enum


class BranchPosition(str, Enum):
    """Spring entity.BranchPosition 대응.

    DB 저장값은 Spring @Enumerated(EnumType.STRING)과 동일하게 enum 멤버 이름
    (예: LEFT_OUTER)이지만, Spring @JsonValue의 code 필드(예: left_outer)와는
    다르다. API 응답 스키마를 만들 때 code 값으로 변환하는 로직
    (예: Pydantic field_serializer)이 반드시 필요하다.

    현재는 ResonanceNodeMaster의 get_stat() 파라미터 타입으로만 쓰인다 — 이 값
    자체를 저장하는 컬럼(user_resonance_nodes.branch_position)은 UserResonanceNode
    도메인 이관 시 여기 매핑된다.
    """

    LEFT_OUTER = "LEFT_OUTER"
    LEFT_INNER = "LEFT_INNER"
    CENTER = "CENTER"
    RIGHT_OUTER = "RIGHT_OUTER"
    RIGHT_INNER = "RIGHT_INNER"

    @property
    def code(self) -> str:
        """Spring @JsonValue의 code 필드 대응 (예: LEFT_OUTER -> left_outer)."""
        return self.value.lower()

    @classmethod
    def from_code(cls, code: str) -> "BranchPosition":
        """code 문자열(예: left_outer)을 멤버로 역변환."""
        return cls[code.upper()]
