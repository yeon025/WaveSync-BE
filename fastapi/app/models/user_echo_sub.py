from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Numeric, Sequence
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, enum_values
from app.models.stat_type import StatType


class UserEchoSub(Base):
    """에코의 서브 옵션.

    id는 user_echo_sub_seq(INCREMENT BY 25) 기반. 매 행마다 nextval()을 호출하며
    batch insert 이득은 db/session.py의 insertmanyvalues_page_size가 담당한다.
    """

    __tablename__ = "user_echo_sub"

    id = Column(
        BigInteger,
        Sequence("user_echo_sub_seq", start=1, increment=25),
        primary_key=True,
    )

    # native_enum=False 필수 — DB 컬럼은 VARCHAR (CLAUDE.md "Enum 처리")
    # 컬럼명 `type`은 DB와 동일하게 유지 (builtin과 겹치지만 인스턴스 속성이라 무방)
    type = Column(SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=False)
    value = Column(Numeric(7, 1), nullable=False)

    is_deleted = Column(Boolean, nullable=False, default=False)

    user_echo_id = Column(BigInteger, ForeignKey("user_echoes.id"), nullable=False)

    user_echo = relationship("UserEcho", back_populates="user_echo_subs")
