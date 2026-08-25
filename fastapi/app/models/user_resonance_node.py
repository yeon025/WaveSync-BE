from sqlalchemy import Column, BigInteger, Boolean, ForeignKey, Sequence
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.branch_position import BranchPosition
from app.models.node_position import NodePosition


class UserResonanceNode(Base):
    """Spring entity.UserResonanceNode 대응.

    id는 user_node_seq(START WITH 1, INCREMENT BY 50, CACHE 50) 기반. Hibernate의
    클라이언트 사이드 hi-lo 채번(nextval() 1회로 50개 블록을 선점)은 SQLAlchemy에
    없어서 여기선 매 행마다 nextval()을 호출한다 — DB 시퀀스가 INCREMENT BY 50이라
    ID 값 자체는 1, 51, 101...로 듬성듬성해지지만(순수 미관상 차이), 왕복 감소는
    db/session.py의 insertmanyvalues_page_size=50이 담당하므로 batch insert 이득은
    동일하게 유지된다. start/increment는 실제 DB 시퀀스 정의를 문서화하는 용도이고
    create_all()을 호출하지 않으므로 시퀀스 생성 자체엔 관여하지 않는다.
    """

    __tablename__ = "user_resonance_nodes"

    id = Column(BigInteger, Sequence("user_node_seq", start=1, increment=50), primary_key=True)

    # native_enum=False 필수 — CLAUDE.md "Enum 처리" 참고 (DB 컬럼은 VARCHAR)
    branch_position = Column(SAEnum(BranchPosition, native_enum=False, length=20), nullable=False)
    node_position = Column(SAEnum(NodePosition, native_enum=False, length=20), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)

    user_resonator_id = Column(BigInteger, ForeignKey("user_resonators.id"), nullable=False)

    # ResonatorService.java(217, 270행)에서 실사용 확인됨 — 양방향 연결
    user_resonator = relationship("UserResonator", back_populates="user_resonance_nodes")
