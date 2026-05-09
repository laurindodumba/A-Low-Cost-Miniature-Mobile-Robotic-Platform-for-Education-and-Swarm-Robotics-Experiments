from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class RemoteProgrammingSendRequest(BaseModel):
    robot_id: Optional[UUID] = None
    group_id: Optional[UUID] = None
    program_id: UUID


class RemoteProgrammingResponse(BaseModel):
    status: str
    message: str