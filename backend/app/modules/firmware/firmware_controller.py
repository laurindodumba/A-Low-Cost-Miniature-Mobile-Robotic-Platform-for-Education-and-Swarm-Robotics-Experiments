import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.firmware.firmware_schema import FirmwareCreateRequest, FirmwareResponse
from app.modules.firmware.firmware_service import FirmwareService

from app.modules.robot.robot_model import Robot
from app.modules.robot.robot_schema import RobotCreate, RobotUpdate, RobotResponse

router = APIRouter(
    prefix="/api/firmware",
    tags=["Firmware"],
)

service = FirmwareService()


@router.post("/upload", response_model=FirmwareResponse)
def upload_firmware(
    request: FirmwareCreateRequest,
    db: Session = Depends(get_db),
):
    return service.create(
        db=db,
        request=request,
    )


@router.get("/files", response_model=list[FirmwareResponse])
def find_firmwares(
    db: Session = Depends(get_db),
):
    return service.find_all(db)


@router.get("/robots")
def list_robots(db: Session = Depends(get_db)):
    return db.query(Robot).order_by(Robot.name).all()


@router.websocket("/send/ws")
async def send_firmware_ws(
    websocket: WebSocket,
    robot_id: str,
    firmware_id: str,
    db: Session = Depends(get_db),
):
    await websocket.accept()

    try:
        async for log in service.flash_firmware_via_cable(
            db=db,
            robot_id=robot_id,
            firmware_id=firmware_id,
        ):
            await websocket.send_text(
                json.dumps({"message": log})
            )

    except WebSocketDisconnect:
        return

    except Exception as error:
        await websocket.send_text(
            json.dumps({"message": f"[ERROR] {error}"})
        )

    finally:
        await websocket.close()