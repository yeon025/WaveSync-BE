from sqlalchemy import JSON, BigInteger, Column, ForeignKey
from sqlalchemy import Enum as SAEnum

from app.db.base import Base, enum_values
from app.resonator.models.scaling_stat import ScalingStat


class ResonatorDamageMaster(Base):
    """점수 계산 대상이 아닌 공명자(서포터 등)는 행이 없다."""

    __tablename__ = "resonator_damage_master"

    id = Column(BigInteger, primary_key=True)

    relevant_damage_types = Column(JSON, nullable=False)

    # native_enum=False 필수 — DB 컬럼은 VARCHAR (CLAUDE.md "Enum 처리")
    scaling_stat = Column(
        SAEnum(ScalingStat, native_enum=False, length=20, values_callable=enum_values), nullable=False
    )

    resonator_master_id = Column(BigInteger, ForeignKey("resonator_master.id"), nullable=False, unique=True)
