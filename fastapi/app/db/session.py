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
    """FastAPI Depends(get_db)로 라우터/서비스에 세션을 주입한다."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
