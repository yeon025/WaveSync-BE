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


def _is_element_damage_type(stat_type: StatType) -> bool:
    return stat_type in _ELEMENT_DAMAGE_TYPES


def _is_basic_or_heavy_damage_type(stat_type: StatType) -> bool:
    return stat_type in _BASIC_OR_HEAVY_DAMAGE_TYPES


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

    if _is_element_damage_type(stat_type) and weapon_master.refine_type == StatType.ALL_ATTRIBUTE_DAMAGE_BONUS:
        percent += refine_value

    if (
        _is_basic_or_heavy_damage_type(stat_type)
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

    return int(Decimal(base_stat) * (Decimal(1) + stat_rate) + Decimal(total_echo_stat))


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


def calculate_final_stat(user_resonator: UserResonator, nodes: List[ResonanceNode]) -> FinalStat:
    """최초 등록용이라 재련 레벨을 1로 고정해 계산한다."""
    user_echoes = user_resonator.user_echoes
    resonator_master = user_resonator.resonator_master
    weapon_master = user_resonator.weapon_master

    return FinalStat(
        hp=_calculate_stat(resonator_master.hp, user_echoes, weapon_master, nodes, StatType.HP_PERCENT, StatType.HP, 1),
        attack=_calculate_stat(
            resonator_master.attack + weapon_master.attack_value,
            user_echoes,
            weapon_master,
            nodes,
            StatType.ATTACK_PERCENT,
            StatType.ATTACK,
            1,
        ),
        defense=_calculate_stat(
            resonator_master.defense, user_echoes, weapon_master, nodes, StatType.DEFENSE_PERCENT, StatType.DEFENSE, 1
        ),
        energy_regen=_calculate_percent_stat(Decimal(100), user_echoes, weapon_master, nodes, StatType.ENERGY_REGEN, 1),
        critical_rate=_calculate_percent_stat(Decimal(5), user_echoes, weapon_master, nodes, StatType.CRITICAL_RATE, 1),
        critical_damage=_calculate_percent_stat(
            Decimal(150), user_echoes, weapon_master, nodes, StatType.CRITICAL_DAMAGE, 1
        ),
        resonance_skill_damage_bonus=_calculate_percent_stat(
            Decimal(0), user_echoes, weapon_master, nodes, StatType.RESONANCE_SKILL_DAMAGE_BONUS, 1
        ),
        basic_attack_damage_bonus=_calculate_percent_stat(
            Decimal(0), user_echoes, weapon_master, nodes, StatType.BASIC_ATTACK_DAMAGE_BONUS, 1
        ),
        heavy_attack_damage_bonus=_calculate_percent_stat(
            Decimal(0), user_echoes, weapon_master, nodes, StatType.HEAVY_ATTACK_DAMAGE_BONUS, 1
        ),
        resonance_liberation_damage_bonus=_calculate_percent_stat(
            Decimal(0), user_echoes, weapon_master, nodes, StatType.RESONANCE_LIBERATION_DAMAGE_BONUS, 1
        ),
        glacio_damage_bonus=_calculate_percent_stat(
            Decimal(0), user_echoes, weapon_master, nodes, StatType.GLACIO_DAMAGE_BONUS, 1
        ),
        fusion_damage_bonus=_calculate_percent_stat(
            Decimal(0), user_echoes, weapon_master, nodes, StatType.FUSION_DAMAGE_BONUS, 1
        ),
        conducto_damage_bonus=_calculate_percent_stat(
            Decimal(0), user_echoes, weapon_master, nodes, StatType.CONDUCTO_DAMAGE_BONUS, 1
        ),
        aero_damage_bonus=_calculate_percent_stat(
            Decimal(0), user_echoes, weapon_master, nodes, StatType.AERO_DAMAGE_BONUS, 1
        ),
        spectra_damage_bonus=_calculate_percent_stat(
            Decimal(0), user_echoes, weapon_master, nodes, StatType.SPECTRA_DAMAGE_BONUS, 1
        ),
        havoc_damage_bonus=_calculate_percent_stat(
            Decimal(0), user_echoes, weapon_master, nodes, StatType.HAVOC_DAMAGE_BONUS, 1
        ),
        healing_bonus=_calculate_percent_stat(Decimal(0), user_echoes, weapon_master, nodes, StatType.HEALING_BONUS, 1),
        user_resonator=user_resonator,
    )


def re_calculate_final_stat(
    required_type: Set[StatType],
    user_resonator: UserResonator,
    nodes: List[ResonanceNode],
    weapon_refine_level: int,
) -> None:
    """required_type의 스탯만 재계산해 final_stat을 in-place로 수정한다 (복합 재련 타입의 파급 대상 포함)."""
    final_stat = user_resonator.final_stat
    user_echoes = user_resonator.user_echoes
    resonator_master = user_resonator.resonator_master
    weapon_master = user_resonator.weapon_master

    required_type = set(required_type)
    if weapon_master.refine_type == StatType.ALL_ATTRIBUTE_DAMAGE_BONUS:
        required_type |= _ELEMENT_DAMAGE_TYPES
    elif weapon_master.refine_type == StatType.BASIC_AND_HEAVY_ATTACK_DAMAGE_BONUS:
        required_type |= _BASIC_OR_HEAVY_DAMAGE_TYPES

    for stat_type in required_type:
        if stat_type == StatType.HP_PERCENT:
            final_stat.hp = _calculate_stat(
                resonator_master.hp,
                user_echoes,
                weapon_master,
                nodes,
                StatType.HP_PERCENT,
                StatType.HP,
                weapon_refine_level,
            )

        elif stat_type == StatType.ATTACK_PERCENT:
            final_stat.attack = _calculate_stat(
                resonator_master.attack + weapon_master.attack_value,
                user_echoes,
                weapon_master,
                nodes,
                StatType.ATTACK_PERCENT,
                StatType.ATTACK,
                weapon_refine_level,
            )

        elif stat_type == StatType.DEFENSE_PERCENT:
            final_stat.defense = _calculate_stat(
                resonator_master.defense,
                user_echoes,
                weapon_master,
                nodes,
                StatType.DEFENSE_PERCENT,
                StatType.DEFENSE,
                weapon_refine_level,
            )

        elif stat_type == StatType.ENERGY_REGEN:
            final_stat.energy_regen = _calculate_percent_stat(
                Decimal(100), user_echoes, weapon_master, nodes, StatType.ENERGY_REGEN, weapon_refine_level
            )

        elif stat_type == StatType.CRITICAL_RATE:
            final_stat.critical_rate = _calculate_percent_stat(
                Decimal(5), user_echoes, weapon_master, nodes, StatType.CRITICAL_RATE, weapon_refine_level
            )

        elif stat_type == StatType.CRITICAL_DAMAGE:
            final_stat.critical_damage = _calculate_percent_stat(
                Decimal(150), user_echoes, weapon_master, nodes, StatType.CRITICAL_DAMAGE, weapon_refine_level
            )

        elif stat_type == StatType.RESONANCE_SKILL_DAMAGE_BONUS:
            final_stat.resonance_skill_damage_bonus = _calculate_percent_stat(
                Decimal(0),
                user_echoes,
                weapon_master,
                nodes,
                StatType.RESONANCE_SKILL_DAMAGE_BONUS,
                weapon_refine_level,
            )

        elif stat_type == StatType.BASIC_ATTACK_DAMAGE_BONUS:
            final_stat.basic_attack_damage_bonus = _calculate_percent_stat(
                Decimal(0), user_echoes, weapon_master, nodes, StatType.BASIC_ATTACK_DAMAGE_BONUS, weapon_refine_level
            )

        elif stat_type == StatType.HEAVY_ATTACK_DAMAGE_BONUS:
            final_stat.heavy_attack_damage_bonus = _calculate_percent_stat(
                Decimal(0), user_echoes, weapon_master, nodes, StatType.HEAVY_ATTACK_DAMAGE_BONUS, weapon_refine_level
            )

        elif stat_type == StatType.RESONANCE_LIBERATION_DAMAGE_BONUS:
            final_stat.resonance_liberation_damage_bonus = _calculate_percent_stat(
                Decimal(0),
                user_echoes,
                weapon_master,
                nodes,
                StatType.RESONANCE_LIBERATION_DAMAGE_BONUS,
                weapon_refine_level,
            )

        elif stat_type == StatType.FUSION_DAMAGE_BONUS:
            final_stat.fusion_damage_bonus = _calculate_percent_stat(
                Decimal(0), user_echoes, weapon_master, nodes, StatType.FUSION_DAMAGE_BONUS, weapon_refine_level
            )

        elif stat_type == StatType.GLACIO_DAMAGE_BONUS:
            final_stat.glacio_damage_bonus = _calculate_percent_stat(
                Decimal(0), user_echoes, weapon_master, nodes, StatType.GLACIO_DAMAGE_BONUS, weapon_refine_level
            )

        elif stat_type == StatType.AERO_DAMAGE_BONUS:
            final_stat.aero_damage_bonus = _calculate_percent_stat(
                Decimal(0), user_echoes, weapon_master, nodes, StatType.AERO_DAMAGE_BONUS, weapon_refine_level
            )

        elif stat_type == StatType.CONDUCTO_DAMAGE_BONUS:
            final_stat.conducto_damage_bonus = _calculate_percent_stat(
                Decimal(0), user_echoes, weapon_master, nodes, StatType.CONDUCTO_DAMAGE_BONUS, weapon_refine_level
            )

        elif stat_type == StatType.SPECTRA_DAMAGE_BONUS:
            final_stat.spectra_damage_bonus = _calculate_percent_stat(
                Decimal(0), user_echoes, weapon_master, nodes, StatType.SPECTRA_DAMAGE_BONUS, weapon_refine_level
            )

        elif stat_type == StatType.HAVOC_DAMAGE_BONUS:
            final_stat.havoc_damage_bonus = _calculate_percent_stat(
                Decimal(0), user_echoes, weapon_master, nodes, StatType.HAVOC_DAMAGE_BONUS, weapon_refine_level
            )

        elif stat_type == StatType.HEALING_BONUS:
            final_stat.healing_bonus = _calculate_percent_stat(
                Decimal(0), user_echoes, weapon_master, nodes, StatType.HEALING_BONUS, weapon_refine_level
            )

        # 나머지 StatType은 무시
