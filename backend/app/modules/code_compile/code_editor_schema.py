from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    name: str


class FileNodeResponse(BaseModel):
    name: str
    path: str
    directory: bool


class FileContentResponse(BaseModel):
    path: str
    content: str


class SaveFileRequest(BaseModel):
    path: str
    content: str


class CreateFileRequest(BaseModel):
    path: str
    content: str | None = ""


class CreateFolderRequest(BaseModel):
    path: str


class DeletePathRequest(BaseModel):
    path: str