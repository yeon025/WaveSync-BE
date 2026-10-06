from typing import Any, Dict, List

from app.resonator.echo_score.echo_grade import EchoGrade
from app.resonator.echo_score.echo_score_calculator import (
    _DAMAGE_TYPE_STAT,
    _SCALING_STAT_TYPE,
    _grade_of,
    build_weight_table,
)
from app.resonator.echo_score.echo_score_service import ScoredEcho
from app.resonator.echo_score.resonator_damage_master import DamageType, ScalingStat
from app.resonator.stat_type import StatType

# overall.summary 등급 집계 순서. EchoGrade 값 자체는 바꾸지 않고 집계 출력 순서만 고정한다.
_GRADE_ORDER = [EchoGrade.SS, EchoGrade.S, EchoGrade.A, EchoGrade.B, EchoGrade.C, EchoGrade.D]

# improvements priority 판단 기준(확보 비율). 기존 점수/등급 계산과는 독립된, Analysis Input 전용 분석 기준이다.
_HIGH_PRIORITY_MAX_RATIO = 0.3
_MEDIUM_PRIORITY_MAX_RATIO = 0.6
_LOW_PRIORITY_MAX_RATIO = 0.85


def _build_overall(scored_echoes: List[ScoredEcho]) -> Dict[str, Any]:
    counts = {grade: 0 for grade in _GRADE_ORDER}
    for scored_echo in scored_echoes:
        counts[scored_echo.echo.grade] += 1

    summary = ", ".join(f"{grade.value} {count}개" for grade, count in counts.items() if count > 0)

    # 종합 등급: 기존 개별 에코 점수(score_percent)의 평균에 기존 등급 기준(GRADE_THRESHOLDS/_grade_of)을
    # 그대로 적용한다. 새로운 가중치나 기준을 추가하지 않는다.
    average_score_percent = sum(se.echo.score_percent for se in scored_echoes) / len(scored_echoes)
    overall_grade = _grade_of(average_score_percent)

    return {"grade": overall_grade.value, "summary": summary}


def _important_stats(relevant_damage_types: List[DamageType], scaling_stat: ScalingStat) -> List[StatType]:
    # 기존 점수 계산 가중치 테이블(build_weight_table)을 그대로 재사용한다.
    # 가중치가 0보다 큰 스탯이 곧 "중요 스탯"이며, 공명효율 포함 여부(피해 타입 1개/2개)도 기존 규칙을 그대로 따른다.
    weight_table = build_weight_table(relevant_damage_types, scaling_stat)

    ordered: List[StatType] = [StatType.CRITICAL_RATE, StatType.CRITICAL_DAMAGE, _SCALING_STAT_TYPE[scaling_stat]]
    ordered.extend(_DAMAGE_TYPE_STAT[damage_type] for damage_type in relevant_damage_types)

    if weight_table[StatType.ENERGY_REGEN] > 0:
        ordered.append(StatType.ENERGY_REGEN)

    return ordered


def _acquisition_ratio(stat_type: StatType, scored_echoes: List[ScoredEcho]) -> float:
    # 기존 서브속성 점수 계산의 normalized_value(최대 롤 대비 비율)를 그대로 가져와,
    # 장착된 에코 전체에 걸쳐 그 스탯이 얼마나 확보됐는지 가늠하는 지표로만 사용한다.
    total_normalized = sum(
        (se.per_stat or {}).get(stat_type.value, {}).get("normalized_value", 0.0) for se in scored_echoes
    )
    return total_normalized / len(scored_echoes)


def _build_improvements(important_stats: List[StatType], scored_echoes: List[ScoredEcho]) -> List[Dict[str, Any]]:
    improvements = []

    for stat_type in important_stats:
        ratio = _acquisition_ratio(stat_type, scored_echoes)

        if ratio < _HIGH_PRIORITY_MAX_RATIO:
            priority, reason = "high", "중요 스탯이며 현재 수치가 낮음"
        elif ratio < _MEDIUM_PRIORITY_MAX_RATIO:
            priority, reason = "medium", "중요 스탯이지만 현재 수치가 보통 수준"
        elif ratio < _LOW_PRIORITY_MAX_RATIO:
            priority, reason = "low", "개선 가치가 있지만 상대적으로 우선순위가 낮음"
        else:
            # 이미 충분히 확보된 스탯은 포함하지 않는다.
            continue

        improvements.append({"stat": stat_type.value, "priority": priority, "reason": reason})

    return improvements


def build_analysis_input(
    relevant_damage_types: List[DamageType],
    scaling_stat: ScalingStat,
    scored_echoes: List[ScoredEcho],
) -> Dict[str, Any]:
    # scored_echoes는 호출부에서 score_percent/grade/per_stat이 모두 채워진 에코만 걸러서 넘겨야 한다.
    important_stats = _important_stats(relevant_damage_types, scaling_stat)

    return {
        "overall": _build_overall(scored_echoes),
        "importantStats": [stat.value for stat in important_stats],
        "improvements": _build_improvements(important_stats, scored_echoes),
    }
