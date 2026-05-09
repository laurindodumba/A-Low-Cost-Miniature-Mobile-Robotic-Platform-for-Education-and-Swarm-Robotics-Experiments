import uuid

from sqlalchemy import Column, String, Integer, LargeBinary, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ProgrammingFile(Base):
    __tablename__ = "programming_files"
    __table_args__ = {"schema": "robot_manager"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(150), nullable=False)
    description = Column(String(1000), nullable=True)

    file_name = Column(String(255), nullable=False)
    content_type = Column(String(120), nullable=False, default="application/octet-stream")
    file_size = Column(Integer, nullable=False)

    file_data = Column(LargeBinary, nullable=False)

    active = Column(Boolean, nullable=False, default=True)