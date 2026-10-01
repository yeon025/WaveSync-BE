import math
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Iterable, Optional, Tuple

from app.config.logger import logger
from app.resonator.echo_score.damage_type import DamageType
from app.resonator.echo_score.scaling_stat import ScalingStat
from app.resonator.echo_score.echo_grade import EchoGrade
from app.resonator.echo_sub_stat_values import VALID_SUB_VALUES
from app.resonator.stat_type import StatType

# 메인/보조 옵션은 제외하고 서브속성만 점수에 반영한다.

# 값을 바꾸면 _EXPECTED_WEIGHT_SUM과 build_weight_table의 공명효율 제외 규칙도 함께 확인해야 한다.
CRIT_DMG_WEIGHT = 2
CRIT_RATE_WEIGHT = 1
ENERGY_REGEN_WEIGHT = 2 / 3
SCALING_STAT_WEIGHT = 2 / 3
DMG_TYPE_WEIGHT = 2 / 3

# 2 + 1 + 2/3 x 3. 피해 타입이 2개면 공명효율 대신 피해 가중치가 하나 더 붙어 합계가 같다.
_EXPECTED_WEIGHT_SUM = 5

# 등급별 최소 점수(%). 키는 EchoGrade 값이며, 최저 기준(C) 미만은 _grade_of가 D로 처리한다.
GRADE_THRESHOLDS = {
    "SS": 75,
    "S": 65,
    "A": 55,
    "B": 45,
    "C": 30,
}

# 등급 판정은 반올림 전 점수로 하되, 부동소수점 누적 오차로 경계값(예: 정확히 75)이 미만으로 뒤집히는 것만 막는다.
_GRADE_EPSILON = 1e-9

_DAMAGE_TYPE_STAT = {
    DamageType.BASIC_ATTACK: StatType.BASIC_ATTACK_DAMAGE_BONUS,
    DamageType.HEAVY_ATTACK: StatType.HEAVY_ATTACK_DAMAGE_BONUS,
    DamageType.RESONANCE_SKILL: StatType.RESONANCE_SKILL_DAMAGE_BONUS,
    DamageType.RESONANCE_LIBERATION: StatType.RESONANCE_LIBERATION_DAMAGE_BONUS,
}

_SCALING_STAT_TYPE = {
    ScalingStat.ATTACK: StatType.ATTACK_PERCENT,
    ScalingStat.DEFENSE: StatType.DEFENSE_PERCENT,
    ScalingStat.HP: StatType.HP_PERCENT,
}

# 저장된 값은 VALID_SUB_VALUES 검증을 거쳤으므로 그 최댓값을 정규화 기준으로 쓴다.
_SUB_V_MAX = {stat_type: float(max(values)) for stat_type, values in VALID_SUB_VALUES.items()}


@dataclass(frozen=True)
class EchoScore:
    """점수 계산 대상이 아니거나 설정이 유효하지 않으면 세 필드 모두 None이다."""

    score_percent: Optional[float] = None
    grade: Optional[EchoGrade] = None
    per_stat: Optional[Dict[str, Dict[str, float]]] = None


def build_weight_table(relevant_damage_types: Iterable[Any], scaling_stat: Any) -> Dict[StatType, float]:
    """JSON 배열 원본(문자열)과 enum 멤버를 모두 받으며, 설정이 유효하지 않으면 ValueError를 낸다."""
    if not isinstance(relevant_damage_types, (list, tuple)):
        raise ValueError(f"relevant_damage_types는 배열이어야 합니다. value={relevant_damage_types!r}")

    damage_types = [DamageType(damage_type) for damage_type in relevant_damage_types]
    if not 1 <= len(damage_types) <= 2:
        raise ValueError(f"relevant_damage_types는 1~2개여야 합니다. value={relevant_damage_types!r}")
    if len(set(damage_types)) != len(damage_types):
        raise ValueError(f"relevant_damage_types에 중복이 있습니다. value={relevant_damage_types!r}")

    scaling = ScalingStat(scaling_stat)

    weights = {stat_type: 0.0 for stat_type in VALID_SUB_VALUES}
    weights[StatType.CRITICAL_DAMAGE] = CRIT_DMG_WEIGHT
    weights[StatType.CRITICAL_RATE] = CRIT_RATE_WEIGHT
    # 피해 타입이 2개면 공명효율은 점수에서 뺀다 (합계를 5로 유지).
    weights[StatType.ENERGY_REGEN] = ENERGY_REGEN_WEIGHT if len(damage_types) == 1 else 0.0
    weights[_SCALING_STAT_TYPE[scaling]] = SCALING_STAT_WEIGHT
    for damage_type in damage_types:
        weights[_DAMAGE_TYPE_STAT[damage_type]] = DMG_TYPE_WEIGHT

    if not math.isclose(sum(weights.values()), _EXPECTED_WEIGHT_SUM):
        raise ValueError(f"가중치 합계가 {_EXPECTED_WEIGHT_SUM}이 아닙니다. sum={sum(weights.values())}")

    return weights


def _grade_of(score_percent: float) -> EchoGrade:
    for grade_name, threshold in sorted(GRADE_THRESHOLDS.items(), key=lambda item: item[1], reverse=True):
        if score_percent + _GRADE_EPSILON >= threshold:
            return EchoGrade(grade_name)
    return EchoGrade.D


def evaluate_echo(sub_stats: Iterable[Tuple[StatType, Decimal]], weight_table: Dict[StatType, float]) -> EchoScore:
    """가중치 테이블이나 정규화 기준에 없는 타입이 섞이면 계산하지 않고 빈 결과를 반환한다."""
    max_score = sum(weight_table.values())
    if max_score <= 0:
        return EchoScore()

    per_stat: Dict[str, Dict[str, float]] = {}
    total = 0.0

    for stat_type, value in sub_stats:
        weight = weight_table.get(stat_type)
        v_max = _SUB_V_MAX.get(stat_type)
        if weight is None or v_max is None:
            logger.warning(f"점수 계산 대상이 아닌 서브속성 타입입니다. type={stat_type}")
            return EchoScore()

        normalized = min(max(float(value) / v_max, 0.0), 1.0)
        contribution = normalized * weight
        total += contribution

        per_stat[stat_type.value] = {
            "value": float(value),
            "normalized_value": round(normalized, 4),
            "weight": round(weight, 4),
            "contribution": round(contribution, 4),
        }

    score_percent = total / max_score * 100

    return EchoScore(score_percent=round(score_percent, 2), grade=_grade_of(score_percent), per_stat=per_stat)
