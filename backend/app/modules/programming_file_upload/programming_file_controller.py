from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.programming_file_upload.programming_file_schema import (
    ProgrammingFileCreateRequest,
    ProgrammingFileResponse,
)
from app.modules.programming_file_upload.programming_file_service import ProgrammingFileService

router = APIRouter(
    prefix="/api/programming-files",
    tags=["Programming Files"],
)

service = ProgrammingFileService()


@router.post("", response_model=ProgrammingFileResponse)
def create_programming_file(
    request: ProgrammingFileCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        return service.create(db, request)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )