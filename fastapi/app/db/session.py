import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# Sequence 기반 PK 모델의 batch insert를 위해 INSERT를 50행 단위로 묶는다.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    insertmanyvalues_page_size=50,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """commit하지 않는다 — yield 이후는 응답 전송 뒤에 실행되므로 commit은 서비스가 응답 생성 전에 직접 한다."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
