import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config.logger import logger
from app.resonator.echo_score import gemini_client, resonator_damage_master_repository

_MAX_EXPLANATION_LENGTH = 1500

_SYSTEM_INSTRUCTION = """\
너는 게임 '명조: 워더링 웨이브'의 에코 서브속성 점수를 사용자에게 설명하는 도우미다.
입력 JSON은 이미 계산이 끝난 결과이며, 너의 역할은 이를 쉬운 한국어로 풀어 설명하는 것뿐이다.

규칙:
- 입력에 있는 점수, 등급, 수치만 인용한다. 점수와 등급을 다시 계산하거나 바꾸지 않는다.
- 입력에 없는 수치, 성능, 추천(교체/육성 등)을 만들어내지 않는다.
- 점수의 의미를 과장하지 않는다. 입력에 없는 정보는 단정하지 않는다.
- 에코를 하나씩 따로 설명하지 말고, 장착된 에코 전체(5개 미만일 수 있다)를 종합한 하나의 분석으로 쓴다.
- 전체적인 점수·등급 분포, 서브속성 기여도가 높았던 항목과 총점의 관계, 캐릭터 정보(피해 유형, 스케일링 스탯)와 연결되는 특징을 설명한다.
- 4~7문장 이내의 하나의 글로, 마크다운 없이 일반 텍스트로 쓴다.
"""


def build_payload(db: Session, resonator_master, echoes: List[Any]) -> Optional[Dict[str, Any]]:
    """점수가 계산된 에코가 없으면(서포터 등) None을 반환한다. commit 전에 호출해 평범한 값으로 확보한다."""
    scored = [echo for echo in echoes if echo.score_percent is not None and echo.per_stat]
    if not scored:
        return None

    damage_master = resonator_damage_master_repository.find_by_resonator_master_id(db, resonator_master.id)
    if damage_master is None:
        return None

    return {
        "resonator": {
            "name": resonator_master.name,
            "element": resonator_master.element.value,
            "relevantDamageTypes": list(damage_master.relevant_damage_types),
            "scalingStat": damage_master.scaling_stat.value,
        },
        "echoes": [
            {
                "name": echo.name,
                "scorePercent": echo.score_percent,
                "grade": echo.grade.value,
                "subStats": echo.per_stat,
            }
            for echo in scored
        ],
    }


def explain(payload: Dict[str, Any]) -> Optional[str]:
    """실패는 부가 기능의 실패일 뿐이라 예외를 올리지 않고 None을 반환한다."""
    try:
        text = gemini_client.generate_text(_SYSTEM_INSTRUCTION, json.dumps(payload, ensure_ascii=False))
    except Exception as e:
        logger.warning(f"에코 설명 생성에 실패했습니다. {e}")
        return None

    text = (text or "").strip()
    if not text:
        logger.warning("Gemini가 빈 응답을 반환했습니다.")
        return None
    if len(text) > _MAX_EXPLANATION_LENGTH:
        logger.warning(f"Gemini 응답이 너무 길어 사용하지 않습니다. length={len(text)}")
        return None

    return text
