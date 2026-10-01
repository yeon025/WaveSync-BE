from enum import Enum


class ScalingStat(str, Enum):
    ATTACK = "attack"
    DEFENSE = "defense"
    HP = "hp"
