from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Numeric, Sequence
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, enum_values
from app.resonator.stat_type import StatType


class UserEchoSub(Base):
    __tablename__ = "user_echo_sub"

    id = Column(
        BigInteger,
        Sequence("user_echo_sub_seq", start=1, increment=25),
        primary_key=True,
    )

    # 속성명이 곧 DB 컬럼명이라 builtin과 겹쳐도 type을 유지한다. native_enum=False 필수 (DB는 VARCHAR).
    type = Column(SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=False)
    value = Column(Numeric(7, 1), nullable=False)

    is_deleted = Column(Boolean, nullable=False, default=False)

    user_echo_id = Column(BigInteger, ForeignKey("user_echoes.id"), nullable=False)

    user_echo = relationship("UserEcho", back_populates="user_echo_subs")
