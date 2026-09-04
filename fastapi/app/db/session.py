import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# insertmanyvalues_page_size:50 — INSERT를 50행 단위로 묶어 전송한다
# (CLAUDE.md "Postgres 최적화 설정"). Sequence 기반 PK 모델과 함께 batch insert에 쓰인다.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    insertmanyvalues_page_size=50,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Depends(get_db)로 세션을 주입한다. commit은 호출부(서비스)에서 명시적으로 수행한다.

    yield 이후 코드는 FastAPI가 응답을 클라이언트로 보낸 뒤 실행되므로, 여기서 commit하면
    commit 실패가 이미 전송된 200 응답을 되돌릴 수 없다 (저장 안 됐는데 성공으로 보이는 정합성 버그).
    따라서 여기서는 미처리 예외에 대한 rollback 안전망만 두고, commit은 응답 생성 전에 서비스가 직접 호출한다.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
