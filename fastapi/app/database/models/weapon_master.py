from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.connection import Base


class WeaponMaster(Base):
    __tablename__ = "weapon_master"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    attack_value: Mapped[int] = mapped_column(Integer, nullable=False)
    main_type: Mapped[str] = mapped_column(String(50), nullable=False)
    main_value: Mapped[float] = mapped_column(Integer, nullable=False)
    refine_type: Mapped[str] = mapped_column(String(50))
    refine_1_value: Mapped[int] = mapped_column(Integer)
    refine_2_value: Mapped[int] = mapped_column(Integer)
    refine_3_value: Mapped[int] = mapped_column(Integer)
    refine_4_value: Mapped[int] = mapped_column(Integer)
    refine_5_value: Mapped[int] = mapped_column(Integer)
    image: Mapped[str] = mapped_column(String(255), nullable=False)