from typing import List, Tuple

import requests

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode

_BASE_URL = "https://api-v2.encore.moe/api/ko"
_TIMEOUT_SECONDS = 10


def _get(path: str) -> dict:
    try:
        response = requests.get(f"{_BASE_URL}{path}", timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        body = e.response.text if e.response is not None else None
        logger.error(f"Encore API 호출 실패: {path}, {e} (body={body})")
        raise CustomException(ErrorCode.EXTERNAL_API_FAILED)

    return response.json()


def download_icon(url: str) -> Tuple[bytes, str]:
    try:
        response = requests.get(url, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        body = e.response.text if e.response is not None else None
        logger.error(f"Encore 이미지 다운로드 실패: {url}, {e} (body={body})")
        raise CustomException(ErrorCode.EXTERNAL_API_FAILED)

    return response.content, response.headers.get("Content-Type", "application/octet-stream")


def get_character_list() -> List[dict]:
    return _get("/character").get("roleList", [])


def get_character_detail(character_id: int) -> dict:
    return _get(f"/character/{character_id}")


def get_weapon_list() -> List[dict]:
    return _get("/weapon").get("weapons", [])


def get_weapon_detail(weapon_id: int) -> dict:
    return _get(f"/weapon/{weapon_id}")


def get_echo_list() -> List[dict]:
    return _get("/echo").get("Echo", [])
