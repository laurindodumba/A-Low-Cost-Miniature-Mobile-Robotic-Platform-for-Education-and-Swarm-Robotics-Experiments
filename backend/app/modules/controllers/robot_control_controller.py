# app/modules/robots/controllers/robot_control_controller.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.controllers.robot_control_schema import (
    RobotControlCommandRequest,
    RobotControlCommandResponse,
)
from app.modules.controllers.robot_control_service import RobotControlService

router = APIRouter(
    prefix="/api/robots",
    tags=["Robot Control"],
)

service = RobotControlService()


@router.post(
    "/{robot_id}/control",
    response_model=RobotControlCommandResponse,
)
def control_robot(
    robot_id: UUID,
    request: RobotControlCommandRequest,
    db: Session = Depends(get_db),
):
    try:
        return service.send_command(
            db=db,
            robot_id=robot_id,
            command=request,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )