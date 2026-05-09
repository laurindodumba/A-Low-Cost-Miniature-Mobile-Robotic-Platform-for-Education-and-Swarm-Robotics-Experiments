import uuid

from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class RobotGroup(Base):
    __table_args__ = {"schema": "robot_manager"}
    __tablename__ = "robot_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(120), nullable=False)
    description = Column(String(500), nullable=True)

    active = Column(Boolean, nullable=False, default=True)

    robots = relationship("Robot", backref="group")