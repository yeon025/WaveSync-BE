from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from app.routers import resonator_router
import logging
from app.exceptions.custom_exception import CustomException
from app.exceptions.exception_handler import (
    custom_exception_handler,
    sqlalchemy_exception_handler,
    global_exception_handler,
)


logging.getLogger("uvicorn").disabled = True
# logging.getLogger("uvicorn.error").disabled = True
logging.getLogger("uvicorn.access").disabled = True


app = FastAPI()

app.include_router(resonator_router.router, prefix="/api")

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
