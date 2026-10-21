from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, enum_values
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

    is_deleted = Column(Boolean, nullable=False, default=False)

    user_resonator_id = Column(BigInteger, ForeignKey("user_resonators.id"), nullable=False)

    user_resonator = relationship("UserResonator", back_populates="user_echoes")
    user_echo_subs = relationship("UserEchoSub", back_populates="user_echo")
