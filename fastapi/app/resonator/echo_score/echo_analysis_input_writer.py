import json
import os
from datetime import datetime
from typing import Any, Dict

# 4단계 상위 = fastapi/. json/은 app 패키지 밖의 리소스 디렉터리다 (images/와 동일한 패턴).
current_file = os.path.abspath(__file__)
echo_score_dir = os.path.dirname(current_file)
resonator_dir = os.path.dirname(echo_score_dir)
app_dir = os.path.dirname(resonator_dir)
BASE_DIR = os.path.dirname(app_dir)
JSON_DIR = os.path.join(BASE_DIR, "json")


def write_analysis_input(user_resonator_id: int, analysis_input: Dict[str, Any]) -> str:
    os.makedirs(JSON_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    file_path = os.path.join(JSON_DIR, f"echo_analysis_input_{user_resonator_id}_{timestamp}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(analysis_input, f, ensure_ascii=False, indent=2)

    return file_path
