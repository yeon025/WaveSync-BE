from fastapi import FastAPI
from app.routers import resonator_router
import logging
from app.exceptions.custom_exception import CustomException
from app.exceptions.exception_handler import custom_exception_handler


logging.getLogger("uvicorn").disabled = True
# logging.getLogger("uvicorn.error").disabled = True
logging.getLogger("uvicorn.access").disabled = True


app = FastAPI()

app.include_router(resonator_router.router, prefix="/api")

app.add_exception_handler(CustomException, custom_exception_handler)