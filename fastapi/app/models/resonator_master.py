from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.element import Element


class ResonatorMaster(Base):
    """Spring entity.ResonatorMaster 대응. 읽기 전용 마스터 데이터."""

    __tablename__ = "resonator_master"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    # native_enum=False 필수 — CLAUDE.md "Enum 처리" 참고 (DB 컬럼은 VARCHAR)
    element = Column(SAEnum(Element, native_enum=False, length=20), nullable=False)

    rarity = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    release_version = Column(Integer, nullable=False)

    thumbnail_image = Column(String(255), nullable=False)
    standing_image = Column(String(255), nullable=True)

    # Spring @OneToOne(mappedBy = "resonatorMaster") 대응
    resonance_node_master = relationship(
        "ResonanceNodeMaster", back_populates="resonator_master", uselist=False
    )

    # Resonator(UserResonator) 도메인을 이관할 때 여기에
    # user_resonators = relationship("UserResonator", back_populates="resonator_master")
    # (Spring @OneToMany(mappedBy = "resonatorMaster") 대응)
    # 를 추가할 것
