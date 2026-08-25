from sqlalchemy import Column, BigInteger, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class FinalStat(Base):
    """Spring entity.FinalStat 대응.

    user_resonator_id는 Spring에서 @OneToOne이지만, 실제 infra/postgres/01_init.sql의
    final_stats.user_resonator_id엔 UNIQUE 제약이 없다(resonance_node_master의
    resonator_master_id와 다름) — DB 정의를 기준으로 unique=True는 넣지 않는다.
    """

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

    user_resonator_id = Column(BigInteger, ForeignKey("user_resonators.id"), nullable=False)
    user_resonator = relationship("UserResonator", back_populates="final_stat")
