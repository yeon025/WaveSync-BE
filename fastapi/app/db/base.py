from sqlalchemy.orm import declarative_base


# 모든 SQLAlchemy 모델이 상속하는 베이스.
#
# 테이블 생성/변경은 infra/postgres/*.sql이 담당하므로 Base.metadata.create_all()은
# 호출하지 않는다 (Spring hibernate.ddl-auto: validate와 동일한 사상 — 스키마는
# SQL 스크립트로만 관리하고, ORM은 이미 존재하는 테이블에 매핑만 한다).
Base = declarative_base()
