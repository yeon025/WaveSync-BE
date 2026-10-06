from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, enum_values
from app.resonator.echo_score.echo_grade import EchoGrade
from app.resonator.stat_type import StatType


class UserEcho(Base):
    __tablename__ = "user_echoes"

    id = Column(BigInteger, primary_key=True)

    name = Column(String(50), nullable=True)

    image = Column(String(255), nullable=True)

    main_type = Column(SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=False)
    main_value = Column(Numeric(5, 1), nullable=False)

    secondary_type = Column(SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=False)
    secondary_value = Column(Integer, nullable=False)

    # 점수 계산 대상이 아닌 공명자의 에코이거나 점수 도입 전 행이면 두 컬럼 모두 NULL이다.
    # per_stat(서브속성별 산출 내역)은 같은 요청 안에서만 쓰이고(Gemini 설명/Analysis Input 생성) 이후 다시
    # 조회되지 않아 DB에는 영속화하지 않는다 (echo_score_service.ScoredEcho로 전달).
    score_percent = Column(Float, nullable=True)
    grade = Column(SAEnum(EchoGrade, native_enum=False, length=2, values_callable=enum_values), nullable=True)

    is_deleted = Column(Boolean, nullable=False, default=False)

    user_resonator_id = Column(BigInteger, ForeignKey("user_resonators.id"), nullable=False)

    user_resonator = relationship("UserResonator", back_populates="user_echoes")
    user_echo_subs = relationship("UserEchoSub", back_populates="user_echo")
