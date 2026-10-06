import os
from typing import Optional

from google import genai
from google.genai import types

from app.config.logger import logger

# Vision 호출 뒤에 붙는 부가 기능이라 오래 기다리지 않는다.
# SDK의 timeout 단위는 밀리초다. Gemini API 서버가 deadline을 10초 미만으로 받지 않으므로 그 이상으로 둔다.
_TIMEOUT_MS = 15000
_DEFAULT_MODEL = "gemini-3.8-flash"


def generate_text(system_instruction: str, prompt: str) -> Optional[str]:
    # Gemini를 정확히 1회 호출한다 (SDK 자동 재시도 끔). API 키가 없으면 호출하지 않고 None을 반환한다.
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY가 설정되지 않아 에코 설명을 생성하지 않습니다.")
        return None

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=_TIMEOUT_MS,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", _DEFAULT_MODEL),
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
            max_output_tokens=1024,
            # 이미 계산된 JSON을 한국어 문장으로 풀어쓰는 단순 작업이라 thinking/함수 호출이 필요 없다.
            # thinking을 꺼야 응답이 빨라져 위 _TIMEOUT_MS(서버 deadline) 내에 안정적으로 끝난다.
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        ),
    )
    return response.text
