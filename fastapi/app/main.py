from fastapi import FastAPI
from routers import resonator_router

app = FastAPI()

app.include_router(resonator_router.router, prefix="/api")