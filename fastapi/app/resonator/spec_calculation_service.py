from decimal import Decimal
from typing import List, Set, Tuple

from app.config.logger import logger
from app.resonator.master.weapon_master import WeaponMaster
from app.resonator.schemas import ResonanceNode
from app.resonator.stat_type import StatType
from app.resonator.user_resonator.final_stat import FinalStat
from app.resonator.user_resonator.user_echo import UserEcho
from app.resonator.user_resonator.user_resonator import UserResonator

# 이미 로드된 UserResonator/ResonanceNode만으로 최종 스탯을 계산하는 순수 함수 모음 (DB I/O 없음).

_HUNDRED = Decimal(100)

_ELEMENT_DAMAGE_TYPES = {
    StatType.GLACIO_DAMAGE_BONUS,
    StatType.FUSION_DAMAGE_BONUS,
    StatType.CONDUCTO_DAMAGE_BONUS,
    StatType.AERO_DAMAGE_BONUS,
    StatType.SPECTRA_DAMAGE_BONUS,
    StatType.HAVOC_DAMAGE_BONUS,
}

_BASIC_OR_HEAVY_DAMAGE_TYPES = {
    StatType.BASIC_ATTACK_DAMAGE_BONUS,
    StatType.HEAVY_ATTACK_DAMAGE_BONUS,
}

_REFINE_VALUE_ATTRS = {
    1: "refine_1_value",
    2: "refine_2_value",
    3: "refine_3_value",
    4: "refine_4_value",
    5: "refine_5_value",
}

# 퍼센트 스탯 → 에코의 고정값 스탯. 이 세 개만 기본 스탯에 곱하는 방식(_calculate_stat)으로 계산한다.
_ECHO_FLAT_TYPES = {
    StatType.HP_PERCENT: StatType.HP,
    StatType.ATTACK_PERCENT: StatType.ATTACK,
    StatType.DEFENSE_PERCENT: StatType.DEFENSE,
}

# 합산 방식(_calculate_percent_stat) 스탯의 기본값. 여기 없는 스탯은 0에서 시작한다.
_PERCENT_BASE_VALUES = {
    StatType.ENERGY_REGEN: Decimal(100),
    StatType.CRITICAL_RATE: Decimal(5),
    StatType.CRITICAL_DAMAGE: Decimal(150),
}

# 계산 대상 StatType → FinalStat 속성. 여기 없는 StatType은 재계산에서 무시한다.
_FINAL_STAT_ATTRS = {
    StatType.HP_PERCENT: "hp",
    StatType.ATTACK_PERCENT: "attack",
    StatType.DEFENSE_PERCENT: "defense",
    StatType.ENERGY_REGEN: "energy_regen",
    StatType.CRITICAL_RATE: "critical_rate",
    StatType.CRITICAL_DAMAGE: "critical_damage",
    StatType.RESONANCE_SKILL_DAMAGE_BONUS: "resonance_skill_damage_bonus",
    StatType.BASIC_ATTACK_DAMAGE_BONUS: "basic_attack_damage_bonus",
    StatType.HEAVY_ATTACK_DAMAGE_BONUS: "heavy_attack_damage_bonus",
    StatType.RESONANCE_LIBERATION_DAMAGE_BONUS: "resonance_liberation_damage_bonus",
    StatType.GLACIO_DAMAGE_BONUS: "glacio_damage_bonus",
    StatType.FUSION_DAMAGE_BONUS: "fusion_damage_bonus",
    StatType.CONDUCTO_DAMAGE_BONUS: "conducto_damage_bonus",
    StatType.AERO_DAMAGE_BONUS: "aero_damage_bonus",
    StatType.SPECTRA_DAMAGE_BONUS: "spectra_damage_bonus",
    StatType.HAVOC_DAMAGE_BONUS: "havoc_damage_bonus",
    StatType.HEALING_BONUS: "healing_bonus",
}


def _get_echo_stat(echoes: List[UserEcho], percent_type: StatType, flat_type: StatType) -> Tuple[Decimal, Decimal]:
    percent = Decimal(0)
    flat = Decimal(0)

    for echo in echoes:
        if echo.main_type == percent_type:
            percent += echo.main_value

        if echo.secondary_type == flat_type:
            flat += Decimal(echo.secondary_value)

        for sub in echo.user_echo_subs:
            if sub.type == percent_type:
                percent += sub.value
            if sub.type == flat_type:
                flat += sub.value

    return percent, flat


def _get_weapon_stat_percent(weapon_master: WeaponMaster, stat_type: StatType, weapon_refine_level: int) -> Decimal:
    percent = Decimal(0)

    attr = _REFINE_VALUE_ATTRS.get(weapon_refine_level)
    if attr is None:
        raise ValueError("잘못된 무기 레벨입니다.")
    refine_value = getattr(weapon_master, attr)

    if weapon_master.main_type == stat_type:
        percent += weapon_master.main_value

    if weapon_master.refine_type == stat_type:
        percent += refine_value

    if stat_type in _ELEMENT_DAMAGE_TYPES and weapon_master.refine_type == StatType.ALL_ATTRIBUTE_DAMAGE_BONUS:
        percent += refine_value

    if (
        stat_type in _BASIC_OR_HEAVY_DAMAGE_TYPES
        and weapon_master.refine_type == StatType.BASIC_AND_HEAVY_ATTACK_DAMAGE_BONUS
    ):
        percent += refine_value

    return percent


def _get_node_stat_percent(nodes: List[ResonanceNode], stat_type: StatType) -> Decimal:
    percent = Decimal(0)

    for node in nodes:
        if node.active and node.stat is not None and node.stat.type == stat_type:
            percent += node.stat.value

    return percent


def _calculate_stat(
    base_stat: int,
    echoes: List[UserEcho],
    weapon_master: WeaponMaster,
    nodes: List[ResonanceNode],
    percent_stat_type: StatType,
    echo_flat_type: StatType,
    weapon_refine_level: int,
) -> int:
    logger.debug(f"{echo_flat_type} baseStat: {base_stat}")

    weapon_stat_percent = _get_weapon_stat_percent(weapon_master, percent_stat_type, weapon_refine_level)
    node_stat_percent = _get_node_stat_percent(nodes, percent_stat_type)

    stat_percent = weapon_stat_percent + node_stat_percent
    logger.debug(f"{echo_flat_type} weapon + node: {stat_percent}%")

    stat_rate = stat_percent / _HUNDRED

    echo_percent, echo_flat = _get_echo_stat(echoes, percent_stat_type, echo_flat_type)

    echo_percent_rate = echo_percent / _HUNDRED

    # 에코 스탯은 최종 합산 전에 따로 int()로 절사(0 방향)한다.
    total_echo_stat = int(Decimal(base_stat) * echo_percent_rate + echo_flat)
    logger.debug(f"{echo_flat_type} echoFlat: {echo_flat}")
    logger.debug(f"{echo_flat_type} echoPercentRate: {echo_percent}%")
    logger.debug(f"{echo_flat_type} totalEchoStat: {total_echo_stat}")

    boosted_stat = Decimal(base_stat) * (Decimal(1) + stat_rate)

    return int(boosted_stat + Decimal(total_echo_stat))


def _calculate_percent_stat(
    base_value: Decimal,
    echoes: List[UserEcho],
    weapon_master: WeaponMaster,
    nodes: List[ResonanceNode],
    stat_type: StatType,
    refine_level: int,
) -> Decimal:
    weapon_stat_percent = _get_weapon_stat_percent(weapon_master, stat_type, refine_level)
    node_stat_percent = _get_node_stat_percent(nodes, stat_type)

    result = base_value + weapon_stat_percent + node_stat_percent

    for echo in echoes:
        if echo.main_type == stat_type:
            result += echo.main_value

        for sub in echo.user_echo_subs:
            if sub.type == stat_type:
                result += sub.value

    logger.debug(f"{stat_type} 최종 스탯 합산 : {result}%")

    return result


def _calculate_final_value(
    stat_type: StatType, user_resonator: UserResonator, nodes: List[ResonanceNode], weapon_refine_level: int
):
    resonator_master = user_resonator.resonator_master
    weapon_master = user_resonator.weapon_master
    echoes = user_resonator.user_echoes

    flat_type = _ECHO_FLAT_TYPES.get(stat_type)
    if flat_type is None:
        base_value = _PERCENT_BASE_VALUES.get(stat_type, Decimal(0))
        return _calculate_percent_stat(base_value, echoes, weapon_master, nodes, stat_type, weapon_refine_level)

    base_stats = {
        StatType.HP_PERCENT: resonator_master.hp,
        StatType.ATTACK_PERCENT: resonator_master.attack + weapon_master.attack_value,
        StatType.DEFENSE_PERCENT: resonator_master.defense,
    }
    base_stat = base_stats[stat_type]
    return _calculate_stat(base_stat, echoes, weapon_master, nodes, stat_type, flat_type, weapon_refine_level)


def calculate_final_stat(user_resonator: UserResonator, nodes: List[ResonanceNode]) -> FinalStat:
    # 최초 등록용이라 재련 레벨을 1로 고정해 계산한다.
    final_values = {
        attr: _calculate_final_value(stat_type, user_resonator, nodes, 1)
        for stat_type, attr in _FINAL_STAT_ATTRS.items()
    }
    return FinalStat(**final_values, user_resonator=user_resonator)


def re_calculate_final_stat(
    required_type: Set[StatType],
    user_resonator: UserResonator,
    nodes: List[ResonanceNode],
    weapon_refine_level: int,
) -> None:
    refine_type = user_resonator.weapon_master.refine_type

    # 복합 재련 타입은 개별 스탯 여러 개에 영향을 주므로 파급 대상까지 재계산한다.
    required_type = set(required_type)
    if refine_type == StatType.ALL_ATTRIBUTE_DAMAGE_BONUS:
        required_type |= _ELEMENT_DAMAGE_TYPES
    elif refine_type == StatType.BASIC_AND_HEAVY_ATTACK_DAMAGE_BONUS:
        required_type |= _BASIC_OR_HEAVY_DAMAGE_TYPES

    for stat_type in required_type:
        attr = _FINAL_STAT_ATTRS.get(stat_type)
        if attr is not None:
            value = _calculate_final_value(stat_type, user_resonator, nodes, weapon_refine_level)
            setattr(user_resonator.final_stat, attr, value)
