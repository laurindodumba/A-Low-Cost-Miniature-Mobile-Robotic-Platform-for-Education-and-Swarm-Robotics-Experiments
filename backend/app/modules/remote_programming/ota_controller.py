from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.programming_file_upload.programming_file_model import ProgrammingFile

router = APIRouter(
    prefix="/api/ota",
    tags=["OTA"],
)


@router.get("/firmware/{program_id}")
def download_firmware(
    program_id: UUID,
    db: Session = Depends(get_db),
):
    program = (
        db.query(ProgrammingFile)
        .filter(ProgrammingFile.id == program_id)
        .first()
    )

    if program is None:
        raise HTTPException(
            status_code=404,
            detail="Programa não encontrado.",
        )

    return Response(
        content=program.file_data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{program.file_name}"'
        },
    )