# app/modules/robots/schemas/robot_control_schema.py

from pydantic import BaseModel, Field


class RobotControlCommandRequest(BaseModel):
    left_x: float = Field(ge=-1, le=1)
    left_y: float = Field(ge=-1, le=1)
    right_x: float = Field(ge=-1, le=1)
    right_y: float = Field(ge=-1, le=1)


class RobotControlCommandResponse(BaseModel):
    robot_id: str
    received: bool
    left_x: float
    left_y: float
    right_x: float
    right_y: float