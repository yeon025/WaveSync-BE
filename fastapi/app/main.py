from fastapi import FastAPI
from app.routers import resonator_router
import logging

logging.getLogger("uvicorn").disabled = True
# logging.getLogger("uvicorn.error").disabled = True
logging.getLogger("uvicorn.access").disabled = True


app = FastAPI()

app.include_router(resonator_router.router, prefix="/api")