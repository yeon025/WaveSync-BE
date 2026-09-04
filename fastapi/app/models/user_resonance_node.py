from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Sequence
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, enum_values
from app.models.branch_position import BranchPosition
from app.models.node_position import NodePosition


class UserResonanceNode(Base):
    """공명자의 공명 노드.

    id는 user_node_seq(INCREMENT BY 50) 기반. 매 행마다 nextval()을 호출하며
    batch insert 이득은 db/session.py의 insertmanyvalues_page_size가 담당한다.
    """

    __tablename__ = "user_resonance_nodes"

    id = Column(BigInteger, Sequence("user_node_seq", start=1, increment=50), primary_key=True)

    # native_enum=False 필수 — DB 컬럼은 VARCHAR (CLAUDE.md "Enum 처리")
    branch_position = Column(
        SAEnum(BranchPosition, native_enum=False, length=20, values_callable=enum_values), nullable=False
    )
    node_position = Column(
        SAEnum(NodePosition, native_enum=False, length=20, values_callable=enum_values), nullable=False
    )

    is_active = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)

    user_resonator_id = Column(BigInteger, ForeignKey("user_resonators.id"), nullable=False)

    user_resonator = relationship("UserResonator", back_populates="user_resonance_nodes")
