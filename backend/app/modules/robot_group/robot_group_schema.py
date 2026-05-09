from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RobotGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RobotGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class RobotGroupResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    active: bool

    class Config:
        from_attributes = True