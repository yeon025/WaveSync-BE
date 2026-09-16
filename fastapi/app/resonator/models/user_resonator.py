from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserResonator(Base):
    """사용자가 등록한 공명자."""

    __tablename__ = "user_resonators"

    id = Column(BigInteger, primary_key=True)

    resonance_chain_level = Column(Integer, nullable=False)
    refine_level = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)

    resonator_master_id = Column(BigInteger, ForeignKey("resonator_master.id"), nullable=False)
    weapon_master_id = Column(BigInteger, ForeignKey("weapon_master.id"), nullable=False)

    # 역방향(user_resonators)이 미사용이라 단방향으로만 연결한다.
    resonator_master = relationship("ResonatorMaster")
    weapon_master = relationship("WeaponMaster")

    final_stat = relationship("FinalStat", uselist=False, back_populates="user_resonator")
    user_resonance_nodes = relationship("UserResonanceNode", back_populates="user_resonator")
    user_echoes = relationship("UserEcho", back_populates="user_resonator")
