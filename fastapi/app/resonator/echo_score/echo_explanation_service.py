import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config.logger import logger
from app.resonator.echo_score import gemini_client, resonator_damage_master_repository
from app.resonator.echo_score.echo_score_service import ScoredEcho

_MAX_EXPLANATION_LENGTH = 1500

_SYSTEM_INSTRUCTION = """
너는 게임 '명조: 워더링 웨이브'의 에코 세팅 분석 결과를 사용자에게 설명하는 도우미다.
입력 JSON은 서버에서 이미 분석이 끝난 결과이며, 너의 역할은 이를 쉬운 한국어로 풀어 설명하는 것뿐이다.

규칙:
- 입력에 있는 등급, 등급 분포, 중요 스탯, 개선 우선순위와 사유만 사용한다.
- 입력에 있는 overall.grade와 overall.summary를 그대로 사용하며, 등급을 다시 계산하거나 변경하지 않는다.
- importantStats에 포함된 스탯은 현재 캐릭터의 에코 세팅에서 중요한 스탯으로 설명한다.
- improvements에 포함된 스탯과 priority를 그대로 사용한다. AI가 자체적으로 우선순위를 변경하지 않는다.
- 입력에 없는 스탯, 수치, 에코 성능, 추천(에코 교체/육성 등)을 만들어내지 않는다.
- 개별 에코를 하나씩 설명하지 않고, 장착된 에코 전체를 종합하여 분석한다.
- 전체적인 등급 분포를 먼저 설명하고, 현재 세팅에서 중요한 스탯과 개선이 필요한 스탯을 연결하여 설명한다.
- improvement의 reason은 그대로 반복하기보다 사용자가 이해하기 쉬운 자연스러운 문장으로 풀어쓴다.
- 입력에 구체적인 스탯 수치가 없다면 수치를 추측하거나 언급하지 않는다.
- 게임의 일반적인 지식을 사용할 수 있지만, 입력 JSON에 없는 사실을 근거로 현재 세팅의 성능을 단정하지 않는다.
- 4~7문장 이내의 하나의 글로 작성한다.
- 마크다운, 목록, 제목을 사용하지 않고 일반 텍스트로 작성한다.
- 분석 결과를 단순히 JSON 내용 그대로 나열하지 말고, 각 정보가 현재 세팅에서 무엇을 의미하는지 자연스럽게 연결해서 설명한다.
"""


def build_payload(db: Session, resonator_master, scored_echoes: List[ScoredEcho]) -> Optional[Dict[str, Any]]:
    # 점수가 계산된 에코가 없으면(서포터 등) None이다. commit 전에 호출해 expire 전의 값으로 확보한다.
    scored = [se for se in scored_echoes if se.echo.score_percent is not None and se.per_stat]

    if not scored:
        return None

    damage_master = resonator_damage_master_repository.find_by_resonator_master_id(db, resonator_master.id)
    if damage_master is None:
        return None

    echo_payloads = []

    for se in scored:
        echo_payloads.append(
            {
                "name": se.echo.name,
                "scorePercent": se.echo.score_percent,
                "grade": se.echo.grade.value,
                "subStats": se.per_stat,
            }
        )

    return {
        "resonator": {
            "name": resonator_master.name,
            "element": resonator_master.element.value,
            "relevantDamageTypes": list(damage_master.relevant_damage_types),
            "scalingStat": damage_master.scaling_stat.value,
        },
        "echoes": echo_payloads,
    }


def explain(payload: Dict[str, Any]) -> Optional[str]:
    # 실패는 부가 기능의 실패일 뿐이라 예외를 올리지 않고 None을 반환한다.
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
