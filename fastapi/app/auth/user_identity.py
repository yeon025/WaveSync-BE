from enum import Enum

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func

from app.db.base import Base, enum_values


class AuthProvider(str, Enum):
    GOOGLE = "google"


class UserIdentity(Base):
    __tablename__ = "user_identities"

    id = Column(BigInteger, primary_key=True)

    # native_enum=False 필수 — DB 컬럼은 VARCHAR (CLAUDE.md "Enum 처리")
    provider = Column(SAEnum(AuthProvider, native_enum=False, length=20, values_callable=enum_values), nullable=False)
    provider_user_id = Column(String(255), nullable=False)

    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
