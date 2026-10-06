from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.resonator.echo_score import resonator_damage_master_repository
from app.resonator.echo_score.echo_score_calculator import EchoScore, build_weight_table, evaluate_echo
from app.resonator.stat_type import StatType
from app.resonator.user_resonator import user_resonator_repository
from app.resonator.user_resonator.user_echo import UserEcho


@dataclass(frozen=True)
class ScoredEcho:
    # per_stat은 DB 컬럼이 아니다 (score_percent/grade만 영속화한다). 같은 요청 안에서 Gemini 설명 payload와
    # Analysis Input을 만드는 데 쓰기 위한 계산 결과를, 그걸 만든 echo와 함께 묶어 전달하는 용도일 뿐이다.
    echo: UserEcho
    per_stat: Optional[Dict[str, Dict[str, float]]]


def _find_weight_table(db: Session, resonator_master_id: int) -> Optional[Dict[StatType, float]]:
    damage_master = resonator_damage_master_repository.find_by_resonator_master_id(db, resonator_master_id)
    if damage_master is None:
        # 서포터 등 점수 계산 대상이 아닌 공명자는 의도적으로 점수를 두지 않는다.
        logger.debug(f"점수 계산 설정이 없는 공명자입니다. resonatorMasterId={resonator_master_id}")
        return None

    try:
        return build_weight_table(damage_master.relevant_damage_types, damage_master.scaling_stat)
    except ValueError as e:
        logger.warning(
            f"점수 계산 설정이 유효하지 않아 점수를 계산하지 않습니다. resonatorMasterId={resonator_master_id}, {e}"
        )
        return None


def compute_and_persist_echo_scores(db: Session, user_resonator_id: int) -> List[ScoredEcho]:
    # commit/flush하지 않는다. autoflush=False라 방금 만든 에코가 대상이면 호출 전에 flush가 필요하다.
    user_resonator = user_resonator_repository.find_by_id_with_echoes(db, user_resonator_id)
    if user_resonator is None:
        raise CustomException(ErrorCode.RESONATOR_NOT_FOUND)

    weight_table = _find_weight_table(db, user_resonator.resonator_master_id)

    scored_echoes = []

    for echo in user_resonator.user_echoes:
        if weight_table is None:
            result = EchoScore()
        else:
            sub_stats = [(sub.type, sub.value) for sub in echo.user_echo_subs]
            result = evaluate_echo(sub_stats, weight_table)

        echo.score_percent = result.score_percent
        echo.grade = result.grade
        scored_echoes.append(ScoredEcho(echo=echo, per_stat=result.per_stat))

    return scored_echoes
