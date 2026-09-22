from sqlalchemy import JSON, BigInteger, Boolean, Column, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, enum_values
from app.resonator.models.echo_grade import EchoGrade
from app.resonator.models.stat_type import StatType


class UserEcho(Base):
    """공명자의 에코."""

    __tablename__ = "user_echoes"

    id = Column(BigInteger, primary_key=True)

    name = Column(String(50), nullable=True)

    image = Column(String(255), nullable=True)

    # native_enum=False 필수 — DB 컬럼은 VARCHAR (CLAUDE.md "Enum 처리")
    main_type = Column(SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=False)
    main_value = Column(Numeric(5, 1), nullable=False)

    secondary_type = Column(SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=False)
    secondary_value = Column(Integer, nullable=False)

    # 서브속성 점수. 점수 계산 대상이 아닌 공명자의 에코이거나 재계산 전인 기존 행은 셋 다 NULL이다.
    # 계산은 공명자 등록 시점에 echo_score_service가 하며, 조회 API는 저장된 값을 그대로 반환한다.
    score_percent = Column(Float, nullable=True)
    grade = Column(SAEnum(EchoGrade, native_enum=False, length=2, values_callable=enum_values), nullable=True)
    per_stat = Column(JSON, nullable=True)

    is_deleted = Column(Boolean, nullable=False, default=False)

    user_resonator_id = Column(BigInteger, ForeignKey("user_resonators.id"), nullable=False)

    user_resonator = relationship("UserResonator", back_populates="user_echoes")
    user_echo_subs = relationship("UserEchoSub", back_populates="user_echo")
