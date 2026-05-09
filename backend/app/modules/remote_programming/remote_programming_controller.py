from uuid import UUID

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.programming_file_upload.programming_file_model import ProgrammingFile
from app.modules.programming_file_upload.programming_file_schema import ProgrammingFileResponse
from app.modules.remote_programming.remote_programming_schema import (
    RemoteProgrammingResponse,
    RemoteProgrammingSendRequest,
)
from app.modules.remote_programming.remote_programming_service import RemoteProgrammingService
from app.modules.robot.robot_model import Robot
from app.modules.robot.robot_schema import RobotResponse
from app.modules.robot_group.robot_group_model import RobotGroup

router = APIRouter(
    prefix="/api/remote-programming",
    tags=["Remote Programming"],
)

service = RemoteProgrammingService()


@router.get("/programs", response_model=list[ProgrammingFileResponse])
def get_programs(db: Session = Depends(get_db)):
    return (
        db.query(ProgrammingFile)
        .filter(ProgrammingFile.active == True)
        .order_by(ProgrammingFile.name.asc())
        .all()
    )


@router.get("/robots", response_model=list[RobotResponse])
def get_robots(db: Session = Depends(get_db)):
    return (
        db.query(Robot)
        .filter(Robot.active == True)
        .order_by(Robot.name.asc())
        .all()
    )


@router.get("/groups")
def get_groups(db: Session = Depends(get_db)):
    groups = (
        db.query(RobotGroup)
        .filter(RobotGroup.active == True)
        .order_by(RobotGroup.name.asc())
        .all()
    )

    return [
        {
            "id": str(group.id),
            "name": group.name,
        }
        for group in groups
    ]


@router.post("/send", response_model=RemoteProgrammingResponse)
def send(
    request: RemoteProgrammingSendRequest,
    db: Session = Depends(get_db),
):
    try:
        return service.send(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ota/send")
def send_ota(
    robot_id: UUID,
    program_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    robot = db.query(Robot).filter(Robot.id == robot_id).first()

    if robot is None:
        raise HTTPException(status_code=404, detail="Robô não encontrado.")

    if not robot.ip:
        raise HTTPException(status_code=400, detail="Robô sem IP cadastrado.")

    program = db.query(ProgrammingFile).filter(
        ProgrammingFile.id == program_id
    ).first()

    if program is None:
        raise HTTPException(status_code=404, detail="Programa não encontrado.")

    base_url = str(request.base_url).rstrip("/")
    firmware_url = f"{base_url}/api/ota/firmware/{program.id}"
    esp_url = f"http://{robot.ip}/ota"

    response = requests.post(
        esp_url,
        params={"url": firmware_url},
        timeout=10,
    )

    if not 200 <= response.status_code < 300:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao iniciar OTA no robô: {response.text}",
        )

    return {
        "status": "SUCCESS",
        "message": "OTA iniciado no robô.",
        "robot_id": str(robot.id),
        "robot_name": robot.name,
        "robot_ip": robot.ip,
        "firmware_url": firmware_url,
    }


@router.post("/ota/broadcast")
def broadcast_ota(
    program_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    program = db.query(ProgrammingFile).filter(
        ProgrammingFile.id == program_id,
        ProgrammingFile.active == True,
    ).first()

    if program is None:
        raise HTTPException(status_code=404, detail="Programa não encontrado.")

    robots = (
        db.query(Robot)
        .filter(Robot.active == True)
        .order_by(Robot.name.asc())
        .all()
    )

    if not robots:
        raise HTTPException(status_code=404, detail="Nenhum robô ativo encontrado.")

    base_url = str(request.base_url).rstrip("/")
    firmware_url = f"{base_url}/api/ota/firmware/{program.id}"

    results = []

    for robot in robots:
        result = _send_ota_to_robot(robot, firmware_url)
        results.append(result)

    success_count = len([r for r in results if r["status"] == "SUCCESS"])
    error_count = len([r for r in results if r["status"] != "SUCCESS"])

    return {
        "status": "DONE",
        "message": "Broadcast OTA finalizado.",
        "program_id": str(program.id),
        "program_name": program.name,
        "firmware_url": firmware_url,
        "total": len(results),
        "success_count": success_count,
        "error_count": error_count,
        "results": results,
    }


def _send_ota_to_robot(robot: Robot, firmware_url: str):
    base_result = {
        "robot_id": str(robot.id),
        "robot_name": robot.name,
        "robot_ip": robot.ip,
    }

    if not robot.ip:
        return {
            **base_result,
            "status": "SKIPPED",
            "message": "Robô sem IP cadastrado.",
        }

    esp_url = f"http://{robot.ip}/ota"

    try:
        response = requests.post(
            esp_url,
            params={"url": firmware_url},
            timeout=10,
        )

        if 200 <= response.status_code < 300:
            return {
                **base_result,
                "status": "SUCCESS",
                "message": "OTA iniciado no robô.",
            }

        return {
            **base_result,
            "status": "ERROR",
            "message": f"Falha ao iniciar OTA: {response.text}",
            "http_status": response.status_code,
        }

    except requests.RequestException as e:
        return {
            **base_result,
            "status": "OFFLINE",
            "message": str(e),
        }