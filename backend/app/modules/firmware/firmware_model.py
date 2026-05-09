import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, LargeBinary, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class FirmwareFile(Base):
    __tablename__ = "firmware_files"
    __table_args__ = {"schema": "robot_manager"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(120), nullable=False)
    description = Column(String(500), nullable=True)

    bootloader_file_name = Column(String(255), nullable=False)
    bootloader_file_data = Column(LargeBinary, nullable=False)
    bootloader_file_size = Column(Integer, nullable=False)

    partitions_file_name = Column(String(255), nullable=False)
    partitions_file_data = Column(LargeBinary, nullable=False)
    partitions_file_size = Column(Integer, nullable=False)

    firmware_file_name = Column(String(255), nullable=False)
    firmware_file_data = Column(LargeBinary, nullable=False)
    firmware_file_size = Column(Integer, nullable=False)

    total_size = Column(Integer, nullable=False)

    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())