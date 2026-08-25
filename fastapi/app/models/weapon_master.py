from sqlalchemy import Column, BigInteger, String, Integer, Numeric
from sqlalchemy import Enum as SAEnum
from app.db.base import Base
from app.models.stat_type import StatType


class WeaponMaster(Base):
    """Spring entity.WeaponMaster 대응. 읽기 전용 마스터 데이터."""

    __tablename__ = "weapon_master"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    attack_value = Column(Integer, nullable=False)

    # native_enum=False 필수 — CLAUDE.md "Enum 처리" 참고 (DB 컬럼은 VARCHAR)
    main_type = Column(SAEnum(StatType, native_enum=False, length=50), nullable=False)
    main_value = Column(Numeric(5, 1), nullable=False)

    refine_type = Column(SAEnum(StatType, native_enum=False, length=50), nullable=True)
    refine_1_value = Column(Numeric(5, 1), nullable=True)
    refine_2_value = Column(Numeric(5, 1), nullable=True)
    refine_3_value = Column(Numeric(5, 1), nullable=True)
    refine_4_value = Column(Numeric(5, 1), nullable=True)
    refine_5_value = Column(Numeric(5, 1), nullable=True)

    image = Column(String(255), nullable=False)

    # UserResonator 도메인을 이관할 때 여기에
    # user_resonators = relationship("UserResonator", back_populates="weapon_master")
    # 추가할 것 (Spring의 @OneToMany(mappedBy = "weaponMaster") 대응)
