from sqlalchemy.orm import declarative_base

# 모든 SQLAlchemy 모델의 베이스. 스키마는 infra/postgres/*.sql이 관리하므로
# create_all()은 호출하지 않고 기존 테이블에 매핑만 한다.
Base = declarative_base()


def enum_values(enum_cls):
    """SAEnum(values_callable=...) 용 — 멤버 이름(대문자)이 아니라 값(소문자)을 DB에 저장하게 한다."""
    return [member.value for member in enum_cls]
