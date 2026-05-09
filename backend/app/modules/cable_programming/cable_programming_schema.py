from uuid import UUID
from pydantic import BaseModel


class CableProgrammingSendRequest(BaseModel):
    robot_id: UUID
    program_id: UUID


class CableProgrammingSendResponse(BaseModel):
    status: str
    message: str