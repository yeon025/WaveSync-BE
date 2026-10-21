from fastapi import Request

from app.config.cors import ALLOWED_ORIGINS
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode

_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
_CSRF_HEADER = "X-WaveSync-Csrf"


def require_csrf_header(request: Request) -> None:
    if request.method.upper() in _SAFE_METHODS:
        return

    # curl 등 비브라우저 클라이언트는 보통 Origin을 보내지 않으므로 이 조건에 걸리지 않는다
    # (관리자 curl 워크플로를 깨지 않기 위함). 브라우저가 보낸 Origin만 허용 목록으로 검증한다.
    origin = request.headers.get("Origin")
    if origin and origin not in ALLOWED_ORIGINS:
        raise CustomException(ErrorCode.FORBIDDEN)

    if request.headers.get(_CSRF_HEADER) != "1":
        raise CustomException(ErrorCode.FORBIDDEN)
