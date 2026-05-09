from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class RobotCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ip: Optional[str] = None
    port: Optional[int] = None
    robot_type: Optional[str] = None


class RobotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ip: Optional[str] = None
    port: Optional[int] = None
    robot_type: Optional[str] = None
    active: Optional[bool] = None
    online: Optional[bool] = None


class RobotResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    ip: Optional[str] = None
    port: Optional[int] = None
    robot_type: Optional[str] = None
    active: bool
    online: bool

    class Config:
        from_attributes = True