import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Robot(Base):
    __tablename__ = "robots"
    __table_args__ = {"schema": "robot_manager"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("robot_manager.robot_groups.id"),
        nullable=True,
    )

    name = Column(String(120), nullable=False)
    description = Column(String(500), nullable=True)

    ip = Column(String(50), nullable=True)
    port = Column(Integer, nullable=True)

    robot_type = Column(String(80), nullable=True)

    active = Column(Boolean, nullable=False, default=True)
    online = Column(Boolean, nullable=False, default=False)