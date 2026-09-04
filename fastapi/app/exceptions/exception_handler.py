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


# CustomException으로 감싸지 않은 DB 접근 예외를 잡는다.
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database Error: {exc}")
    return _error_response(ErrorCode.DATABASE_ERROR)


# catch-all. 더 구체적인 핸들러(CustomException/SQLAlchemyError)가 먼저 잡으므로 나머지만 온다.
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled Exception", exc_info=exc)
    return _error_response(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(exc))
