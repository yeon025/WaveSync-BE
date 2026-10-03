from enum import Enum

from sqlalchemy import JSON, BigInteger, Column, ForeignKey
from sqlalchemy import Enum as SAEnum

from app.db.base import Base, enum_values


class DamageType(str, Enum):
    # SAEnum 컬럼이 아니라 resonator_damage_master.relevant_damage_types(JSON 배열)의 원소 값이다.
    BASIC_ATTACK = "basic_attack"
    HEAVY_ATTACK = "heavy_attack"
    RESONANCE_SKILL = "resonance_skill"
    RESONANCE_LIBERATION = "resonance_liberation"


class ScalingStat(str, Enum):
    ATTACK = "attack"
    DEFENSE = "defense"
    HP = "hp"


class ResonatorDamageMaster(Base):
    # 점수 계산 대상이 아닌 공명자(서포터 등)는 행이 없다.
    __tablename__ = "resonator_damage_master"

    id = Column(BigInteger, primary_key=True)

    relevant_damage_types = Column(JSON, nullable=False)

    scaling_stat = Column(
        SAEnum(ScalingStat, native_enum=False, length=20, values_callable=enum_values), nullable=False
    )

    resonator_master_id = Column(BigInteger, ForeignKey("resonator_master.id"), nullable=False, unique=True)
