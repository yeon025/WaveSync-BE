from sqlalchemy import Column, BigInteger, Numeric, Boolean, ForeignKey, Sequence
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.stat_type import StatType


class UserEchoSub(Base):
    """Spring entity.UserEchoSub 대응.

    id는 user_echo_sub_seq(START WITH 1, INCREMENT BY 50, CACHE 50) 기반.
    user_resonance_node.py와 동일한 원칙: Hibernate hi-lo 채번은 재현하지 않고
    매 행마다 nextval()을 호출한다 — ID 값은 듬성듬성해지지만(순수 미관상 차이),
    batch insert 왕복 감소는 db/session.py의 insertmanyvalues_page_size=50이
    담당한다. start/increment는 실제 DB 시퀀스 정의를 문서화하는 용도이고
    create_all()을 호출하지 않으므로 시퀀스 생성 자체엔 관여하지 않는다.
    """

    __tablename__ = "user_echo_sub"

    id = Column(BigInteger, Sequence("user_echo_sub_seq", start=1, increment=50), primary_key=True)

    # native_enum=False 필수 — CLAUDE.md "Enum 처리" 참고 (DB 컬럼은 VARCHAR)
    # 컬럼명은 DB/Spring과 동일하게 `type` 유지 (Python builtin과 이름만 겹칠 뿐, 인스턴스
    # 속성이라 문제 없음)
    type = Column(SAEnum(StatType, native_enum=False, length=50), nullable=False)
    value = Column(Numeric(7, 1), nullable=False)

    is_deleted = Column(Boolean, nullable=False, default=False)

    user_echo_id = Column(BigInteger, ForeignKey("user_echoes.id"), nullable=False)

    # SpecCalculationService.java 실사용 확인됨 — 양방향 연결
    user_echo = relationship("UserEcho", back_populates="user_echo_subs")
