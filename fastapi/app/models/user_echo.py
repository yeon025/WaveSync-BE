from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, Numeric
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, enum_values
from app.models.stat_type import StatType


class UserEcho(Base):
    """공명자의 에코."""

    __tablename__ = "user_echoes"

    id = Column(BigInteger, primary_key=True)

    # native_enum=False 필수 — DB 컬럼은 VARCHAR (CLAUDE.md "Enum 처리")
    main_type = Column(SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=False)
    main_value = Column(Numeric(5, 1), nullable=False)

    secondary_type = Column(SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=False)
    secondary_value = Column(Integer, nullable=False)

    is_deleted = Column(Boolean, nullable=False, default=False)

    user_resonator_id = Column(BigInteger, ForeignKey("user_resonators.id"), nullable=False)

    user_resonator = relationship("UserResonator", back_populates="user_echoes")
    user_echo_subs = relationship("UserEchoSub", back_populates="user_echo")
