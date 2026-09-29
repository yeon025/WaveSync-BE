from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode


def _error_response(error_code: ErrorCode, detail: str = None) -> JSONResponse:
    status_code, code, message = error_code.value
    content = {"code": code, "message": message}
    if detail is not None:
        content["detail"] = detail
    return JSONResponse(status_code=status_code, content=content)


async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
        },
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database Error: {exc}")
    return _error_response(ErrorCode.DATABASE_ERROR)


# Starlette가 예외 타입별로 더 구체적인 핸들러를 먼저 고르므로 나머지 예외만 여기로 온다.
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled Exception", exc_info=exc)
    return _error_response(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(exc))
