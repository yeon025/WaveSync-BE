from decimal import Decimal
from typing import List, Set, Tuple

from app.config.logger import logger
from app.models.final_stat import FinalStat
from app.models.stat_type import StatType
from app.models.user_echo import UserEcho
from app.models.user_resonator import UserResonator
from app.models.weapon_master import WeaponMaster
from app.schemas.common import ResonanceNode

# Spring service.SpecCalculationService 대응.
# DB I/O 없음 — 이미 로드된 UserResonator/ResonanceNode만으로 계산하는 순수 함수 모음.
# 클래스로 감싸지 않은 이유: Spring도 상태 없는 @Service(인스턴스 필드 없음)이고,
# 지금까지 FastAPI services/의 함수형 컨벤션(resonator_profile_service 등)과도 일치.


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


# 에코에서 획득한 백분율 스탯과 고정 스탯을 합산 (메인/보조/서브 전부)
def _get_echo_stat(
    echoes: List[UserEcho], percent_type: StatType, flat_type: StatType
) -> Tuple[Decimal, Decimal]:
    percent = Decimal(0)
    flat = Decimal(0)

    for echo in echoes:
        # 메인 옵션의 백분율 스탯 합산
        if echo.main_type == percent_type:
            percent += echo.main_value

        # 보조 옵션의 고정 스탯 합산
        if echo.secondary_type == flat_type:
            flat += Decimal(echo.secondary_value)

        # 서브 옵션의 백분율 스탯 및 고정 스탯 합산
        for sub in echo.user_echo_subs:
            if sub.type == percent_type:
                percent += sub.value
            if sub.type == flat_type:
                flat += sub.value

    return percent, flat


# 무기에서 획득한 백분율 스탯 합산
def _get_weapon_stat_percent(
    weapon_master: WeaponMaster, stat_type: StatType, weapon_refine_level: int
) -> Decimal:
    percent = Decimal(0)

    attr = _REFINE_VALUE_ATTRS.get(weapon_refine_level)
    if attr is None:
        raise ValueError("잘못된 무기 레벨입니다.")
    refine_value = getattr(weapon_master, attr)

    # 무기 주 옵션
    if weapon_master.main_type == stat_type:
        percent += weapon_master.main_value

    # 무기 재련 옵션
    if weapon_master.refine_type == stat_type:
        percent += refine_value

    # 전체 속성 피해 보너스
    if (
        _is_element_damage_type(stat_type)
        and weapon_master.refine_type == StatType.ALL_ATTRIBUTE_DAMAGE_BONUS
    ):
        percent += refine_value

    # 일반 공격 + 강공격 피해 보너스
    if (
        _is_basic_or_heavy_damage_type(stat_type)
        and weapon_master.refine_type == StatType.BASIC_AND_HEAVY_ATTACK_DAMAGE_BONUS
    ):
        percent += refine_value

    return percent


# 공명 노드에서 획득한 백분율 스탯 합산
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

    # 무기에서 획득한 백분율 스탯
    weapon_stat_percent = _get_weapon_stat_percent(
        weapon_master, percent_stat_type, weapon_refine_level
    )

    # 공명 노드에서 획득한 백분율 스탯
    node_stat_percent = _get_node_stat_percent(nodes, percent_stat_type)

    # 무기와 공명 노드의 백분율 스탯 합산
    stat_percent = weapon_stat_percent + node_stat_percent
    logger.debug(f"{echo_flat_type} weapon + node: {stat_percent}%")

    # 백분율 스탯을 소수로 변환 (30 -> 0.30)
    stat_rate = stat_percent / _HUNDRED

    # 에코에서 획득한 백분율 스탯과 고정 스탯
    echo_percent, echo_flat = _get_echo_stat(echoes, percent_stat_type, echo_flat_type)

    # 에코 백분율을 소수로 변환 (22 -> 0.22)
    echo_percent_rate = echo_percent / _HUNDRED

    # 에코 스탯 계산 = 기초 스탯 x 에코 백분율 + 에코 고정 스탯
    # BigDecimal.intValue()는 0 방향으로 절사 — Python도 Decimal에 int()로 동일하게 절사
    total_echo_stat = int(Decimal(base_stat) * echo_percent_rate + echo_flat)
    logger.debug(f"{echo_flat_type} echoFlat: {echo_flat}")
    logger.debug(f"{echo_flat_type} echoPercentRate: {echo_percent}%")
    logger.debug(f"{echo_flat_type} totalEchoStat: {total_echo_stat}")

    # 최종 스탯 = 기초 스탯 x (1 + 백분율 스탯) + 에코 스탯
    return int(Decimal(base_stat) * (Decimal(1) + stat_rate) + Decimal(total_echo_stat))


def _calculate_percent_stat(
    base_value: Decimal,
    echoes: List[UserEcho],
    weapon_master: WeaponMaster,
    nodes: List[ResonanceNode],
    stat_type: StatType,
    refine_level: int,
) -> Decimal:
    # 무기에서 획득한 백분율 스탯
    weapon_stat_percent = _get_weapon_stat_percent(weapon_master, stat_type, refine_level)

    # 공명 노드에서 획득한 백분율 스탯
    node_stat_percent = _get_node_stat_percent(nodes, stat_type)

    # 기본 수치 + 무기 + 공명 노드
    result = base_value + weapon_stat_percent + node_stat_percent

    # 에코 메인 옵션, 서브 옵션에서 획득한 스탯 합산
    for echo in echoes:
        if echo.main_type == stat_type:
            result += echo.main_value

        for sub in echo.user_echo_subs:
            if sub.type == stat_type:
                result += sub.value

    logger.debug(f"{stat_type} 최종 스탯 합산 : {result}%")

    return result


def calculate_final_stat(user_resonator: UserResonator, nodes: List[ResonanceNode]) -> FinalStat:
    """공명자 최초 등록 시 스펙 전체 계산. 재련레벨 1 고정 (createResonator 대응)."""
    user_echoes = user_resonator.user_echoes
    resonator_master = user_resonator.resonator_master
    weapon_master = user_resonator.weapon_master

    return FinalStat(
        hp=_calculate_stat(
            resonator_master.hp,
            user_echoes,
            weapon_master,
            nodes,
            StatType.HP_PERCENT,
            StatType.HP,
            1,
        ),
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
            resonator_master.defense,
            user_echoes,
            weapon_master,
            nodes,
            StatType.DEFENSE_PERCENT,
            StatType.DEFENSE,
            1,
        ),
        energy_regen=_calculate_percent_stat(
            Decimal(100), user_echoes, weapon_master, nodes, StatType.ENERGY_REGEN, 1
        ),
        critical_rate=_calculate_percent_stat(
            Decimal(5), user_echoes, weapon_master, nodes, StatType.CRITICAL_RATE, 1
        ),
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
            Decimal(0),
            user_echoes,
            weapon_master,
            nodes,
            StatType.RESONANCE_LIBERATION_DAMAGE_BONUS,
            1,
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
        healing_bonus=_calculate_percent_stat(
            Decimal(0), user_echoes, weapon_master, nodes, StatType.HEALING_BONUS, 1
        ),
        user_resonator=user_resonator,
    )


def re_calculate_final_stat(
    required_type: Set[StatType],
    user_resonator: UserResonator,
    nodes: List[ResonanceNode],
    weapon_refine_level: int,
) -> None:
    """updateResonator 대응 — required_type에 담긴 스탯만 부분 재계산해 final_stat을 in-place 수정한다.

    Spring 원본과 동일하게 아래 11개 StatType만 처리한다. ENERGY_REGEN,
    RESONANCE_SKILL_DAMAGE_BONUS, BASIC_ATTACK_DAMAGE_BONUS, HEAVY_ATTACK_DAMAGE_BONUS,
    RESONANCE_LIBERATION_DAMAGE_BONUS는 Spring switch에도 없어서 재계산되지 않는다
    (Spring 원본 동작 그대로 보존 — 버그로 보이더라도 임의로 고치지 않음).
    """
    final_stat = user_resonator.final_stat
    user_echoes = user_resonator.user_echoes
    resonator_master = user_resonator.resonator_master
    weapon_master = user_resonator.weapon_master

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

        elif stat_type == StatType.CRITICAL_RATE:
            final_stat.critical_rate = _calculate_percent_stat(
                Decimal(5),
                user_echoes,
                weapon_master,
                nodes,
                StatType.CRITICAL_RATE,
                weapon_refine_level,
            )

        elif stat_type == StatType.CRITICAL_DAMAGE:
            final_stat.critical_damage = _calculate_percent_stat(
                Decimal(150),
                user_echoes,
                weapon_master,
                nodes,
                StatType.CRITICAL_DAMAGE,
                weapon_refine_level,
            )

        elif stat_type == StatType.FUSION_DAMAGE_BONUS:
            final_stat.fusion_damage_bonus = _calculate_percent_stat(
                Decimal(0),
                user_echoes,
                weapon_master,
                nodes,
                StatType.FUSION_DAMAGE_BONUS,
                weapon_refine_level,
            )

        elif stat_type == StatType.GLACIO_DAMAGE_BONUS:
            final_stat.glacio_damage_bonus = _calculate_percent_stat(
                Decimal(0),
                user_echoes,
                weapon_master,
                nodes,
                StatType.GLACIO_DAMAGE_BONUS,
                weapon_refine_level,
            )

        elif stat_type == StatType.AERO_DAMAGE_BONUS:
            final_stat.aero_damage_bonus = _calculate_percent_stat(
                Decimal(0),
                user_echoes,
                weapon_master,
                nodes,
                StatType.AERO_DAMAGE_BONUS,
                weapon_refine_level,
            )

        elif stat_type == StatType.CONDUCTO_DAMAGE_BONUS:
            final_stat.conducto_damage_bonus = _calculate_percent_stat(
                Decimal(0),
                user_echoes,
                weapon_master,
                nodes,
                StatType.CONDUCTO_DAMAGE_BONUS,
                weapon_refine_level,
            )

        elif stat_type == StatType.SPECTRA_DAMAGE_BONUS:
            final_stat.spectra_damage_bonus = _calculate_percent_stat(
                Decimal(0),
                user_echoes,
                weapon_master,
                nodes,
                StatType.SPECTRA_DAMAGE_BONUS,
                weapon_refine_level,
            )

        elif stat_type == StatType.HAVOC_DAMAGE_BONUS:
            final_stat.havoc_damage_bonus = _calculate_percent_stat(
                Decimal(0),
                user_echoes,
                weapon_master,
                nodes,
                StatType.HAVOC_DAMAGE_BONUS,
                weapon_refine_level,
            )

        elif stat_type == StatType.HEALING_BONUS:
            final_stat.healing_bonus = _calculate_percent_stat(
                Decimal(0),
                user_echoes,
                weapon_master,
                nodes,
                StatType.HEALING_BONUS,
                weapon_refine_level,
            )

        # 나머지 StatType은 Spring 원본의 default -> {} 와 동일하게 무시
