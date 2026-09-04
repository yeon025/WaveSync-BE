from sqlalchemy import BigInteger, Column, Integer, Numeric, String
from sqlalchemy import Enum as SAEnum

from app.db.base import Base, enum_values
from app.models.stat_type import StatType


class WeaponMaster(Base):
    """무기 마스터 데이터 (읽기 전용)."""

    __tablename__ = "weapon_master"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    attack_value = Column(Integer, nullable=False)

    # native_enum=False 필수 — DB 컬럼은 VARCHAR (CLAUDE.md "Enum 처리")
    main_type = Column(SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=False)
    main_value = Column(Numeric(5, 1), nullable=False)

    refine_type = Column(SAEnum(StatType, native_enum=False, length=50, values_callable=enum_values), nullable=True)
    refine_1_value = Column(Numeric(5, 1), nullable=True)
    refine_2_value = Column(Numeric(5, 1), nullable=True)
    refine_3_value = Column(Numeric(5, 1), nullable=True)
    refine_4_value = Column(Numeric(5, 1), nullable=True)
    refine_5_value = Column(Numeric(5, 1), nullable=True)

    image = Column(String(255), nullable=False)

    # 역참조(user_resonators)는 미사용이라 추가하지 않는다 (UserResonator 쪽에서 단방향 연결).
