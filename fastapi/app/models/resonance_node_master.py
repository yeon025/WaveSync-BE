from sqlalchemy import BigInteger, Column, ForeignKey, Numeric
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, enum_values
from app.models.stat_type import StatType


class ResonanceNodeMaster(Base):
    """공명 노드 마스터 데이터 (읽기 전용).

    노드 스탯 선택 로직은 mapper/resonance_node_mapper.py의 get_stat()에 있다.
    """

    __tablename__ = "resonance_node_master"

    id = Column(BigInteger, primary_key=True)

    # native_enum=False 필수 — DB 컬럼은 VARCHAR (CLAUDE.md "Enum 처리")
    outer_node_type = Column(
        SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=False
    )
    outer_top_node_value = Column(Numeric(5, 1), nullable=False)
    outer_middle_node_value = Column(Numeric(5, 1), nullable=False)

    inner_node_type = Column(
        SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=False
    )
    inner_top_node_value = Column(Numeric(5, 1), nullable=False)
    inner_middle_node_value = Column(Numeric(5, 1), nullable=False)

    resonator_master_id = Column(BigInteger, ForeignKey("resonator_master.id"), nullable=False, unique=True)
    resonator_master = relationship("ResonatorMaster", back_populates="resonance_node_master")
