import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# Hibernate jdbc.batch_size:50 대응 — INSERT를 페이지 단위로 묶어서 전송한다.
# (CLAUDE.md "Postgres 최적화 설정" 참고). WeaponMaster는 읽기 전용이라 지금은
# 쓰이지 않지만, 엔진 레벨 설정이라 나중에 쓰기가 많은 도메인(Resonator 등)이
# 이 세션을 그대로 재사용하면 자동으로 적용된다.
#
# SEQUENCE(INCREMENT BY 50, CACHE 50) 기반 batch insert 패턴은 테이블별 PK
# 전략이라 엔진에서 미리 잡을 수 없다. 나중에 쓰기 도메인을 옮길 때 모델에서
# Column(BigInteger, Sequence("xxx_seq", start=1, increment=50), primary_key=True)
# 형태로 재현할 것 (infra/postgres/01_init.sql의 user_echo_sub_seq, user_node_seq 참고).
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
