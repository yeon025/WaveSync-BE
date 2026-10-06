from typing import List, Optional

from sqlalchemy.orm import Session

from app.config.logger import logger
from app.resonator.echo_score import resonator_damage_master_repository
from app.resonator.echo_score.echo_analysis_input_builder import build_analysis_input
from app.resonator.echo_score.echo_analysis_input_writer import write_analysis_input
from app.resonator.echo_score.echo_score_service import ScoredEcho
from app.resonator.echo_score.resonator_damage_master import DamageType, ScalingStat


def generate_and_write(
    db: Session, resonator_master_id: int, user_resonator_id: int, scored_echoes: List[ScoredEcho]
) -> Optional[str]:
    # 점수가 계산된 에코가 없으면(서포터 등) Analysis Input을 만들지 않는다. commit 전에 호출해 expire 전 값을 쓴다.
    scored = [
        se for se in scored_echoes if se.echo.score_percent is not None and se.echo.grade is not None and se.per_stat
    ]

    if not scored:
        return None

    damage_master = resonator_damage_master_repository.find_by_resonator_master_id(db, resonator_master_id)
    if damage_master is None:
        return None

    relevant_damage_types = [DamageType(damage_type) for damage_type in damage_master.relevant_damage_types]
    scaling_stat = ScalingStat(damage_master.scaling_stat)

    analysis_input = build_analysis_input(relevant_damage_types, scaling_stat, scored)

    try:
        return write_analysis_input(user_resonator_id, analysis_input)
    except OSError as e:
        # Gemini 분석을 위한 파생 데이터일 뿐이라, 파일 저장 실패가 공명자 등록 전체를 실패시키지 않는다.
        logger.warning(f"Analysis Input 파일 저장에 실패했습니다. userResonatorId={user_resonator_id}, {e}")
        return None
