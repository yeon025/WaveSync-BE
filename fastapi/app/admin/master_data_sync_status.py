from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.db.base import Base


class MasterDataSyncStatus(Base):
    __tablename__ = "master_data_sync_status"

    # SyncTarget.value(resonators 등)를 그대로 쓴다 — 대상 하나당 가장 최근 실행 결과만 1행으로 유지한다.
    target = Column(String(30), primary_key=True)

    synced_at = Column(DateTime(timezone=True), nullable=False)
    success = Column(Boolean, nullable=False)

    created = Column(Integer, nullable=True)
    updated = Column(Integer, nullable=True)
    unchanged = Column(Integer, nullable=True)
    skipped = Column(Integer, nullable=True)

    error_message = Column(String(500), nullable=True)
