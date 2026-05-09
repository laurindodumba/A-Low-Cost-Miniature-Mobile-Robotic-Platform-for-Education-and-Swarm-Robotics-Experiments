from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.robot.robot_model import Robot
from app.modules.robot.robot_schema import RobotCreate, RobotUpdate, RobotResponse

router = APIRouter(
    prefix="/api/robots",
    tags=["Robots"]
)


@router.post("", response_model=RobotResponse, status_code=status.HTTP_201_CREATED)
def create_robot(data: RobotCreate, db: Session = Depends(get_db)):
    robot = Robot(**data.model_dump())

    db.add(robot)
    db.commit()
    db.refresh(robot)

    return robot


@router.get("", response_model=list[RobotResponse])
def list_robots(db: Session = Depends(get_db)):
    return db.query(Robot).order_by(Robot.name).all()


@router.get("/{robot_id}", response_model=RobotResponse)
def get_robot(robot_id: UUID, db: Session = Depends(get_db)):
    robot = db.query(Robot).filter(Robot.id == robot_id).first()

    if robot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Robô não encontrado"
        )

    return robot


@router.put("/{robot_id}", response_model=RobotResponse)
def update_robot(robot_id: UUID, data: RobotUpdate, db: Session = Depends(get_db)):
    robot = db.query(Robot).filter(Robot.id == robot_id).first()

    if robot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Robô não encontrado"
        )

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(robot, field, value)

    db.commit()
    db.refresh(robot)

    return robot


@router.delete("/{robot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_robot(robot_id: UUID, db: Session = Depends(get_db)):
    robot = db.query(Robot).filter(Robot.id == robot_id).first()

    if robot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Robô não encontrado"
        )

    db.delete(robot)
    db.commit()

    return None