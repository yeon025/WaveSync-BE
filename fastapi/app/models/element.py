from enum import Enum


class Element(str, Enum):
    """공명자 속성(원소) 종류. 멤버 이름은 대문자, 값(DB/API 노출값)은 소문자다.

    값 <-> 멤버 변환은 code / from_code로 한다. SAEnum 컬럼엔 values_callable=enum_values 필수.
    """

    GLACIO = "glacio"
    FUSION = "fusion"
    AERO = "aero"
    CONDUCTO = "conducto"
    SPECTRA = "spectra"
    HAVOC = "havoc"

    @property
    def code(self) -> str:
        """API/DB 노출용 값 (예: glacio)."""
        return self.value

    @classmethod
    def from_code(cls, code: str) -> "Element":
        """값(예: glacio)을 멤버로 역변환."""
        return cls(code)
