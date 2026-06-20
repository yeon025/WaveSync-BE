from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.connection import Base


class ResonatorMaster(Base):
    __tablename__ = "resonator_master"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    element: Mapped[str] = mapped_column(String(20), nullable=False)
    rarity: Mapped[int] = mapped_column(Integer, nullable=False)
    hp: Mapped[int] = mapped_column(Integer, nullable=False)
    attack: Mapped[int] = mapped_column(Integer, nullable=False)
    defense: Mapped[int] = mapped_column(Integer, nullable=False)
    release_version: Mapped[int] = mapped_column(Integer, nullable=False)
    thumbnail_image: Mapped[str] = mapped_column(String(255), nullable=False)
    standing_image: Mapped[str] = mapped_column(String(255))