from enum import Enum


class Element(str, Enum):
    GLACIO = "glacio"
    FUSION = "fusion"
    AERO = "aero"
    CONDUCTO = "conducto"
    SPECTRA = "spectra"
    HAVOC = "havoc"

    @property
    def code(self) -> str:
        return self.value

    @classmethod
    def from_code(cls, code: str) -> "Element":
        return cls(code)
