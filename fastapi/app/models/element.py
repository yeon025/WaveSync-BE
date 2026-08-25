from enum import Enum


class Element(str, Enum):
    """Spring entity.Element 대응.

    DB 저장값은 Spring @Enumerated(EnumType.STRING)과 동일하게 enum 멤버 이름
    (예: GLACIO)이지만, Spring @JsonValue의 code 필드(예: glacio)와는 다르다.
    Resonator 도메인에서 API 응답 스키마를 만들 때 code 값으로 변환하는 로직
    (예: Pydantic field_serializer)이 반드시 필요하다.
    """

    GLACIO = "GLACIO"
    FUSION = "FUSION"
    AERO = "AERO"
    CONDUCTO = "CONDUCTO"
    SPECTRA = "SPECTRA"
    HAVOC = "HAVOC"

    @property
    def code(self) -> str:
        """Spring @JsonValue의 code 필드 대응 (예: GLACIO -> glacio)."""
        return self.value.lower()

    @classmethod
    def from_code(cls, code: str) -> "Element":
        """code 문자열(예: glacio)을 멤버로 역변환."""
        return cls[code.upper()]
