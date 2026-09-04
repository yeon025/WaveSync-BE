import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.exception_handler import (
    custom_exception_handler,
    global_exception_handler,
    sqlalchemy_exception_handler,
)
from app.routers import resonator_router

logging.getLogger("uvicorn").disabled = True
# logging.getLogger("uvicorn.error").disabled = True
logging.getLogger("uvicorn.access").disabled = True


app = FastAPI()

# CORS 허용 origin/method/header
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://resocollector.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# 요청 시작/응답 완료 시각을 로그로 남긴다.
@app.middleware("http")
async def execution_time_middleware(request: Request, call_next):
    # 헬스체크는 주기적으로 들어오므로 실행시간 로그에서 제외한다.
    if request.url.path == "/health":
        return await call_next(request)

    start = time.perf_counter()
    logger.info(f"{request.method} {request.url.path} 요청을 시작합니다.")

    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = int((time.perf_counter() - start) * 1000)
        status = response.status_code if response is not None else 500
        logger.info(
            f"{request.method} {request.url.path} 응답이 완료되었습니다. | status={status} | time={duration_ms}ms"
        )


app.include_router(resonator_router.router, prefix="/api")

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
