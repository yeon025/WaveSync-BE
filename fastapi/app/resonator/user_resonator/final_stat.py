from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from app.db.base import Base


class FinalStat(Base):
    __tablename__ = "final_stats"

    id = Column(BigInteger, primary_key=True)

    hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)

    energy_regen = Column(Numeric(5, 1), nullable=False)
    critical_rate = Column(Numeric(5, 1), nullable=False)
    critical_damage = Column(Numeric(5, 1), nullable=False)

    resonance_skill_damage_bonus = Column(Numeric(5, 1), nullable=False)
    basic_attack_damage_bonus = Column(Numeric(5, 1), nullable=False)
    heavy_attack_damage_bonus = Column(Numeric(5, 1), nullable=False)
    resonance_liberation_damage_bonus = Column(Numeric(5, 1), nullable=False)

    glacio_damage_bonus = Column(Numeric(5, 1), nullable=False)
    fusion_damage_bonus = Column(Numeric(5, 1), nullable=False)
    conducto_damage_bonus = Column(Numeric(5, 1), nullable=False)
    aero_damage_bonus = Column(Numeric(5, 1), nullable=False)
    spectra_damage_bonus = Column(Numeric(5, 1), nullable=False)
    havoc_damage_bonus = Column(Numeric(5, 1), nullable=False)
    healing_bonus = Column(Numeric(5, 1), nullable=False)

    # UserResonator.final_stat을 1:1(uselist=False)로 다루므로 UNIQUE로 DB에서도 보장한다.
    user_resonator_id = Column(BigInteger, ForeignKey("user_resonators.id"), nullable=False, unique=True)
    user_resonator = relationship("UserResonator", back_populates="final_stat")
