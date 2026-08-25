from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode
from app.config.logger import logger


def _error_response(error_code: ErrorCode, detail: str = None) -> JSONResponse:
    status_code, code, message = error_code.value
    content = {"code": code, "message": message}
    if detail is not None:
        content["detail"] = detail
    return JSONResponse(status_code=status_code, content=content)


async def custom_exception_handler(
    request: Request,
    exc: CustomException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
        },
    )


# Spring GlobalExceptionHandler.handleDataAccessException 대응.
# CustomException으로 감싸지 않은, DB 접근 중 발생한 예외만 여기서 잡는다.
async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
):
    logger.error(f"Database Error: {exc}")
    return _error_response(ErrorCode.DATABASE_ERROR)


# Spring GlobalExceptionHandler.handleException 대응 — catch-all.
# CustomException/SQLAlchemyError는 각자의 전용 핸들러가 먼저 잡으므로 여기엔 오지 않는다
# (Starlette가 예외 타입의 MRO를 보고 가장 구체적인 핸들러를 고르기 때문).
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.error("Unhandled Exception", exc_info=exc)
    return _error_response(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(exc))
