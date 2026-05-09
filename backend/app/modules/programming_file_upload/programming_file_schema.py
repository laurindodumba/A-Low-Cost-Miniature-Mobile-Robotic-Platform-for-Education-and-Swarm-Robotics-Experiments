from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProgrammingFileCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=1000)

    file_name: str = Field(min_length=1, max_length=255)
    content_type: str = Field(default="application/octet-stream", max_length=120)
    file_size: int = Field(gt=0)
    file_base64: str = Field(min_length=1)


class ProgrammingFileResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    file_name: str
    content_type: str
    file_size: int
    active: bool

    class Config:
        from_attributes = True