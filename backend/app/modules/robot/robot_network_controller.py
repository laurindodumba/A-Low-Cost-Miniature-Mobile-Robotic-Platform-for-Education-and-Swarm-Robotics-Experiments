import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.robot.robot_model import Robot
from app.modules.robot.robot_schema import RobotResponse

router = APIRouter(
    prefix="/api/robots/network",
    tags=["Robots Network"]
)


def _get_network_prefix() -> str:
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    parts = local_ip.split(".")
    return f"{parts[0]}.{parts[1]}.{parts[2]}"


def _check_robot(ip: str, port: int = 8080):
    try:
        response = requests.get(
            f"http://{ip}:{port}/health",
            timeout=0.7,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("device") != "robot":
            return None

        return {
            "name": data.get("name", f"Robô {ip}"),
            "description": data.get("description"),
            "ip": ip,
            "port": port,
            "robot_type": data.get("type", "ESP32"),
            "active": True,
            "online": True,
        }
    except Exception:
        return None


@router.get("/scan")
def scan_robots(mock: bool = True):
    # 🔹 modo mock (ex: /scan?mock=true)
    if mock:
        return {
            "network": "192.168.0.0/24",
            "total": 2,
            "robots": [
                {
                    "name": "Robo Alpha",
                    "description": "ESP32 teste",
                    "ip": "192.168.0.101",
                    "port": 8080,
                    "robot_type": "ESP32",
                    "active": True,
                    "online": True,
                },
                {
                    "name": "Robo Beta",
                    "description": "Arduino teste",
                    "ip": "192.168.0.102",
                    "port": 8080,
                    "robot_type": "Arduino",
                    "active": True,
                    "online": False,
                },
            ],
        }

    # 🔹 modo real
    prefix = _get_network_prefix()
    found = []

    with ThreadPoolExecutor(max_workers=80) as executor:
        futures = [
            executor.submit(_check_robot, f"{prefix}.{i}")
            for i in range(1, 255)
        ]

        for future in as_completed(futures):
            robot = future.result()
            if robot:
                found.append(robot)

    return {
        "network": f"{prefix}.0/24",
        "total": len(found),
        "robots": found,
    }


@router.post("/refresh-status", response_model=list[RobotResponse])
def refresh_status(db: Session = Depends(get_db)):
    robots = db.query(Robot).order_by(Robot.name).all()

    for robot in robots:
        if not robot.ip:
            robot.online = False
            continue

        port = robot.port or 8080

        try:
            response = requests.get(
                f"http://{robot.ip}:{port}/health",
                timeout=1.5,
            )

            robot.online = response.status_code == 200
        except Exception:
            robot.online = False

    db.commit()

    for robot in robots:
        db.refresh(robot)

    return robots