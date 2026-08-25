from sqlalchemy import Column, BigInteger, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class UserResonator(Base):
    """Spring entity.UserResonator 대응."""

    __tablename__ = "user_resonators"

    id = Column(BigInteger, primary_key=True)

    resonance_chain_level = Column(Integer, nullable=False)
    refine_level = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)

    resonator_master_id = Column(BigInteger, ForeignKey("resonator_master.id"), nullable=False)
    weapon_master_id = Column(BigInteger, ForeignKey("weapon_master.id"), nullable=False)

    # ResonatorMaster.userResonators/WeaponMaster.userResonators는 Spring에서도
    # 실제로 쓰이지 않는 미사용 필드라 back_populates 없이 단방향으로만 연결한다
    # (resonator_master.py/weapon_master.py는 수정하지 않음)
    resonator_master = relationship("ResonatorMaster")
    weapon_master = relationship("WeaponMaster")
