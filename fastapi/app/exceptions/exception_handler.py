from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.custom_exception import CustomException


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