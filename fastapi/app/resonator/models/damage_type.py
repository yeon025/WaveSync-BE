from enum import Enum


class DamageType(str, Enum):
    """공명자가 주로 쓰는 피해 타입. 멤버 이름은 대문자, 값(DB/API 노출값)은 소문자다.

    resonator_damage_master.relevant_damage_types(JSON 배열)의 원소 값이다.
    대응하는 에코 서브속성(StatType) 매핑은 resonator/echo_score_service.py에 있다.
    """

    BASIC_ATTACK = "basic_attack"
    HEAVY_ATTACK = "heavy_attack"
    RESONANCE_SKILL = "resonance_skill"
    RESONANCE_LIBERATION = "resonance_liberation"
