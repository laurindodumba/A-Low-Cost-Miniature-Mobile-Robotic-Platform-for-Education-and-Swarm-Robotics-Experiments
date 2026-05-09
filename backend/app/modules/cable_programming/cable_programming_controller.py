from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.modules.cable_programming.cable_programming_schema import (
    CableProgrammingSendRequest,
    CableProgrammingSendResponse,
)
from app.modules.cable_programming.cable_programming_service import (
    CableProgrammingService,
)
from app.modules.programming_file_upload.programming_file_model import ProgrammingFile
from app.modules.programming_file_upload.programming_file_schema import (
    ProgrammingFileResponse,
)
from app.modules.robot.robot_model import Robot
from app.modules.robot.robot_schema import RobotResponse

router = APIRouter(
    prefix="/api/cable-programming",
    tags=["Cable Programming"],
)

service = CableProgrammingService()


@router.get("/programs", response_model=list[ProgrammingFileResponse])
def get_programs(db: Session = Depends(get_db)):
    return db.query(ProgrammingFile).filter(
        ProgrammingFile.active == True
    ).order_by(ProgrammingFile.name.asc()).all()


@router.get("/robots", response_model=list[RobotResponse])
def get_robots(db: Session = Depends(get_db)):
    return db.query(Robot).filter(
        Robot.active == True
    ).order_by(Robot.name.asc()).all()


@router.post("/send", response_model=CableProgrammingSendResponse)
def send_program(
    request: CableProgrammingSendRequest,
    db: Session = Depends(get_db),
):
    try:
        service.find_robot(db, request.robot_id)
        service.find_program(db, request.program_id)

        return CableProgrammingSendResponse(
            status="READY",
            message="Programa pronto para gravação.",
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.websocket("/send/ws")
async def send_program_ws(
    websocket: WebSocket,
    robot_id: UUID,
    program_id: UUID,
):
    await websocket.accept()

    db = SessionLocal()

    try:
        async for log in service.stream_flash_logs(db, robot_id, program_id):
            await websocket.send_text(log)

    except WebSocketDisconnect:
        pass

    finally:
        db.close()
        try:
            await websocket.close()
        except RuntimeError:
            pass