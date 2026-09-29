from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Sequence
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, enum_values
from app.resonator.models.branch_position import BranchPosition
from app.resonator.models.node_position import NodePosition


class UserResonanceNode(Base):
    __tablename__ = "user_resonance_nodes"

    id = Column(BigInteger, Sequence("user_node_seq", start=1, increment=10), primary_key=True)

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
