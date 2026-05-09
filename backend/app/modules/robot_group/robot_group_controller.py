from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.robot.robot_schema import RobotResponse
from app.modules.robot_group.robot_group_schema import (
    RobotGroupCreate,
    RobotGroupUpdate,
    RobotGroupResponse,
)
from app.modules.robot_group.robot_group_service import RobotGroupService

router = APIRouter(
    prefix="/api/robot-groups",
    tags=["Robot Groups"],
)

service = RobotGroupService()


@router.post(
    "",
    response_model=RobotGroupResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_group(
    data: RobotGroupCreate,
    db: Session = Depends(get_db),
):
    return service.create(data, db)


@router.get(
    "",
    response_model=list[RobotGroupResponse],
)
def list_groups(
    db: Session = Depends(get_db),
):
    return service.list_active(db)


@router.get(
    "/{group_id}",
    response_model=RobotGroupResponse,
)
def get_group(
    group_id: UUID,
    db: Session = Depends(get_db),
):
    return service.get_active_by_id(group_id, db)


@router.put(
    "/{group_id}",
    response_model=RobotGroupResponse,
)
def update_group(
    group_id: UUID,
    data: RobotGroupUpdate,
    db: Session = Depends(get_db),
):
    return service.update(group_id, data, db)


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def safe_delete_group(
    group_id: UUID,
    db: Session = Depends(get_db),
):
    service.safe_delete(group_id, db)
    return None


@router.get(
    "/{group_id}/robots",
    response_model=list[RobotResponse],
)
def list_group_robots(
    group_id: UUID,
    db: Session = Depends(get_db),
):
    return service.list_robots(group_id, db)


@router.post(
    "/{group_id}/robots/{robot_id}",
    response_model=RobotResponse,
)
def add_robot_to_group(
    group_id: UUID,
    robot_id: UUID,
    db: Session = Depends(get_db),
):
    return service.add_robot(group_id, robot_id, db)


@router.delete(
    "/{group_id}/robots/{robot_id}",
    response_model=RobotResponse,
)
def remove_robot_from_group(
    group_id: UUID,
    robot_id: UUID,
    db: Session = Depends(get_db),
):
    return service.remove_robot(group_id, robot_id, db)