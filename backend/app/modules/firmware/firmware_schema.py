from uuid import UUID

from pydantic import BaseModel


class FirmwareBinaryRequest(BaseModel):
    file_name: str
    content_type: str | None = None
    file_size: int
    file_base64: str


class FirmwareCreateRequest(BaseModel):
    name: str
    description: str | None = None

    bootloader: FirmwareBinaryRequest
    partitions: FirmwareBinaryRequest
    firmware: FirmwareBinaryRequest


class FirmwareResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None

    bootloader_file_name: str
    partitions_file_name: str
    firmware_file_name: str

    total_size: int
    active: bool

    class Config:
        from_attributes = True