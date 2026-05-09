from fastapi import APIRouter, HTTPException

from app.modules.code_compile.code_editor_schema import (
    CreateProjectRequest,
    SaveFileRequest,
    CreateFileRequest,
    CreateFolderRequest,
)
from app.modules.code_compile.code_editor_service import CodeEditorService

router = APIRouter(
    prefix="/api/code-editor",
    tags=["Code Editor"],
)

service = CodeEditorService()


@router.get("/projects")
def find_projects():
    return service.find_projects()


@router.post("/projects")
def create_project(request: CreateProjectRequest):
    try:
        return service.create_project(request.name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/projects/{project}/tree")
def get_tree(project: str):
    try:
        return service.get_tree(project)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/projects/{project}/file")
def read_file(project: str, path: str):
    try:
        return service.read_file(project, path)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.put("/projects/{project}/file")
def save_file(project: str, request: SaveFileRequest):
    try:
        return service.save_file(
            project=project,
            path=request.path,
            content=request.content,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/projects/{project}/file")
def create_file(project: str, request: CreateFileRequest):
    try:
        return service.create_file(
            project=project,
            path=request.path,
            content=request.content or "",
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/projects/{project}/folder")
def create_folder(project: str, request: CreateFolderRequest):
    try:
        return service.create_folder(
            project=project,
            path=request.path,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.delete("/projects/{project}/path")
def delete_path(project: str, path: str):
    try:
        return service.delete_path(project, path)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))