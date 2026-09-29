import math
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.resonator.echo_score_weights import (
    CRIT_DMG_WEIGHT,
    CRIT_RATE_WEIGHT,
    DMG_TYPE_WEIGHT,
    ENERGY_REGEN_WEIGHT,
    GRADE_THRESHOLDS,
    SCALING_STAT_WEIGHT,
)
from app.resonator.echo_sub_stat_values import VALID_SUB_VALUES
from app.resonator.models.damage_type import DamageType
from app.resonator.models.echo_grade import EchoGrade
from app.resonator.models.scaling_stat import ScalingStat
from app.resonator.models.stat_type import StatType
from app.resonator.repositories import resonator_damage_master_repository, user_resonator_repository

# 에코 서브속성 점수 계산. 메인/보조 메인 옵션은 점수에서 제외하고 서브속성만 본다.
# build_weight_table / evaluate_echo는 DB I/O 없는 순수 함수이고, compute_and_persist_echo_scores만 DB를 쓴다.

# 정상적인 가중치 테이블의 합계 (2 + 1 + 2/3 x 3).
# 피해 타입 1개: 공명효율 2/3 + 기준 스탯 2/3 + 피해 2/3 / 피해 타입 2개: 공명효율 0 + 기준 스탯 2/3 + 피해 2/3 x 2
_EXPECTED_WEIGHT_SUM = 5

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

# 서브속성 1개의 최대 유효 수치 (정규화 기준). 생성 시 검증(VALID_SUB_VALUES)을 통과한 값만 저장되므로 그 최댓값과 같다.
_SUB_V_MAX = {stat_type: float(max(values)) for stat_type, values in VALID_SUB_VALUES.items()}


@dataclass(frozen=True)
class EchoScore:
    """에코 1개의 점수 계산 결과. 계산 불가(대상 아님/유효하지 않은 설정)면 세 필드 모두 None이다."""

    score_percent: Optional[float] = None
    grade: Optional[EchoGrade] = None
    per_stat: Optional[Dict[str, Dict[str, float]]] = None


def build_weight_table(relevant_damage_types: Iterable[Any], scaling_stat: Any) -> Dict[StatType, float]:
    """피해 타입과 기준 스탯으로 서브속성별 가중치 테이블을 만든다 (순수 함수).

    반환값은 VALID_SUB_VALUES의 13개 서브속성 전부를 키로 가지며 가중치가 없는 항목은 0이다.
    JSON 배열 원본(문자열 리스트)과 enum 멤버 모두 받는다. 유효하지 않은 설정이면 ValueError.
    """
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
    """GRADE_THRESHOLDS를 기준으로 등급을 매긴다.

    각 등급은 [threshold, 다음으로 높은 threshold) 구간이며 비교는 ">="만 쓴다
    (예: SS=75, S=65면 65<=score<75가 S). 최저 threshold(C=30) 미만은 EchoGrade.D.
    """
    for grade_name, threshold in sorted(GRADE_THRESHOLDS.items(), key=lambda item: item[1], reverse=True):
        if score_percent + _GRADE_EPSILON >= threshold:
            return EchoGrade(grade_name)
    return EchoGrade.D


def evaluate_echo(sub_stats: Iterable[Tuple[StatType, Decimal]], weight_table: Dict[StatType, float]) -> EchoScore:
    """에코 서브속성 (타입, 값) 목록으로 점수/등급/per_stat을 계산한다 (순수 함수).

    normalized = value / v_max (0~1로 clamp), contribution = normalized x weight,
    score_percent = sum(contribution) / sum(weight) x 100.
    per_stat은 에코가 가진 서브속성만 담으며 가중치 0인 항목도 포함한다.
    가중치 테이블/정규화 기준에 없는 타입이 섞여 있으면 계산하지 않고 빈 결과(None)를 반환한다.
    """
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


def _find_weight_table(db: Session, resonator_master_id: int) -> Optional[Dict[StatType, float]]:
    damage_master = resonator_damage_master_repository.find_by_resonator_master_id(db, resonator_master_id)
    if damage_master is None:
        # 서포터 등 점수 계산 대상이 아닌 공명자 (의도된 설계) — 점수는 null로 둔다.
        logger.debug(f"점수 계산 설정이 없는 공명자입니다. resonatorMasterId={resonator_master_id}")
        return None

    try:
        return build_weight_table(damage_master.relevant_damage_types, damage_master.scaling_stat)
    except ValueError as e:
        logger.warning(
            f"점수 계산 설정이 유효하지 않아 점수를 계산하지 않습니다. resonatorMasterId={resonator_master_id}, {e}"
        )
        return None


def compute_and_persist_echo_scores(db: Session, user_resonator_id: int) -> None:
    """공명자의 에코별 점수/등급/per_stat을 계산해 UserEcho에 세팅한다.

    commit/flush 없음 — 호출자의 트랜잭션 경계에 속한다 (같은 트랜잭션에서 에코와 함께 커밋된다).
    autoflush=False이므로 방금 만든 에코를 대상으로 하려면 호출 전에 db.flush()가 필요하다.
    점수 계산 대상이 아니거나 설정이 유효하지 않으면 세 필드를 모두 None으로 둔다.
    """
    user_resonator = user_resonator_repository.find_by_id_with_echoes(db, user_resonator_id)
    if user_resonator is None:
        raise CustomException(ErrorCode.RESONATOR_NOT_FOUND)

    weight_table = _find_weight_table(db, user_resonator.resonator_master_id)

    for echo in user_resonator.user_echoes:
        if weight_table is None:
            result = EchoScore()
        else:
            sub_stats: List[Tuple[StatType, Decimal]] = [(sub.type, sub.value) for sub in echo.user_echo_subs]
            result = evaluate_echo(sub_stats, weight_table)

        echo.score_percent = result.score_percent
        echo.grade = result.grade
        echo.per_stat = result.per_stat
