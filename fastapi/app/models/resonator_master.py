from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base, enum_values
from app.models.element import Element


class ResonatorMaster(Base):
    """공명자 마스터 데이터 (읽기 전용)."""

    __tablename__ = "resonator_master"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    # native_enum=False 필수 — DB 컬럼은 VARCHAR (CLAUDE.md "Enum 처리")
    element = Column(SAEnum(Element, native_enum=False, length=20, values_callable=enum_values), nullable=False)

    rarity = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    release_version = Column(Integer, nullable=False)

    thumbnail_image = Column(String(255), nullable=False)
    standing_image = Column(String(255), nullable=True)

    resonance_node_master = relationship("ResonanceNodeMaster", back_populates="resonator_master", uselist=False)

    # 역참조(user_resonators)는 미사용이라 추가하지 않는다 (UserResonator 쪽에서 단방향 연결).
