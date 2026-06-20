import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "wawu")
POSTGRES_USER = os.getenv("POSTGRES_USER", "wawu")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "wawu")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# 엔진
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# 세션
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()