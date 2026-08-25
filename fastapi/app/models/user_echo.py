from sqlalchemy import Column, BigInteger, Integer, Numeric, Boolean, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.stat_type import StatType


class UserEcho(Base):
    """Spring entity.UserEcho 대응."""

    __tablename__ = "user_echoes"

    id = Column(BigInteger, primary_key=True)

    # native_enum=False 필수 — CLAUDE.md "Enum 처리" 참고 (DB 컬럼은 VARCHAR)
    main_type = Column(SAEnum(StatType, native_enum=False, length=50), nullable=False)
    main_value = Column(Numeric(5, 1), nullable=False)

    secondary_type = Column(SAEnum(StatType, native_enum=False, length=50), nullable=False)
    secondary_value = Column(Integer, nullable=False)

    is_deleted = Column(Boolean, nullable=False, default=False)

    user_resonator_id = Column(BigInteger, ForeignKey("user_resonators.id"), nullable=False)

    # UserResonator.user_echoes는 아직 없어 단방향으로만 연결
    # (UserResonator 쪽 back_populates는 그 필드를 실제로 쓰는 시점에 연결)
    user_resonator = relationship("UserResonator")
