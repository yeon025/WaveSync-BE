from enum import Enum


class Element(str, Enum):
    """Spring entity.Element 대응.

    DB 저장값은 Spring @Enumerated(EnumType.STRING)과 동일하게 enum 멤버 이름
    (예: GLACIO)이다.
    """

    GLACIO = "GLACIO"
    FUSION = "FUSION"
    AERO = "AERO"
    CONDUCTO = "CONDUCTO"
    SPECTRA = "SPECTRA"
    HAVOC = "HAVOC"
