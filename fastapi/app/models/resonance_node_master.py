from sqlalchemy import BigInteger, Column, ForeignKey, Numeric
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.stat_type import StatType


class ResonanceNodeMaster(Base):
    """Spring entity.ResonanceNodeMaster 대응. 읽기 전용 마스터 데이터.

    getStat(branchPosition, nodePosition)은 순수 selector라 여기엔 옮기지 않고
    app/mapper/resonance_node_mapper.py의 get_stat() 함수로 분리했다.
    """

    __tablename__ = "resonance_node_master"

    id = Column(BigInteger, primary_key=True)

    # native_enum=False 필수 — CLAUDE.md "Enum 처리" 참고 (DB 컬럼은 VARCHAR)
    outer_node_type = Column(SAEnum(StatType, native_enum=False, length=50), nullable=False)
    outer_top_node_value = Column(Numeric(5, 1), nullable=False)
    outer_middle_node_value = Column(Numeric(5, 1), nullable=False)

    inner_node_type = Column(SAEnum(StatType, native_enum=False, length=50), nullable=False)
    inner_top_node_value = Column(Numeric(5, 1), nullable=False)
    inner_middle_node_value = Column(Numeric(5, 1), nullable=False)

    resonator_master_id = Column(BigInteger, ForeignKey("resonator_master.id"), nullable=False, unique=True)
    resonator_master = relationship("ResonatorMaster", back_populates="resonance_node_master")
