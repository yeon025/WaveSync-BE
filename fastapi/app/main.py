import logging
import time

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.config.cors import ALLOWED_ORIGINS
from app.config.logger import logger
from app.db.session import get_db
from app.exceptions.custom_exception import CustomException
from app.exceptions.exception_handler import (
    custom_exception_handler,
    global_exception_handler,
    sqlalchemy_exception_handler,
)
from app.resonator.router import router as resonator_router

logging.getLogger("uvicorn").disabled = True
logging.getLogger("uvicorn.access").disabled = True


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    # UptimeRobot 등 외부 모니터링이 주기적으로 호출해 DB를 깨워두는 용도도 겸한다.
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        # 내부 오류나 접속 정보는 응답에 노출하지 않는다.
        return JSONResponse(status_code=503, content={"status": "unhealthy", "database": "disconnected"})


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


app.include_router(auth_router, prefix="/api")
app.include_router(resonator_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
