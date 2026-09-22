from enum import Enum


class ScalingStat(str, Enum):
    """공명자의 스킬 배율이 붙는 기준 스탯. 멤버 이름은 대문자, 값(DB 저장값)은 소문자다.

    SAEnum 컬럼엔 values_callable=enum_values 필수.
    """

    ATTACK = "attack"
    DEFENSE = "defense"
    HP = "hp"
