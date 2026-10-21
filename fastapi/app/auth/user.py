from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func

from app.auth.user_role import UserRole
from app.db.base import Base, enum_values


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)

    role = Column(
        SAEnum(UserRole, native_enum=False, length=10, values_callable=enum_values),
        nullable=False,
        default=UserRole.USER,
    )

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
