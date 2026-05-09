from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.robot.robot_model import Robot
from app.modules.robot_group.robot_group_model import RobotGroup
from app.modules.robot_group.robot_group_schema import (
    RobotGroupCreate,
    RobotGroupUpdate,
)


class RobotGroupService:

    def create(self, data: RobotGroupCreate, db: Session) -> RobotGroup:
        group = RobotGroup(**data.model_dump())

        db.add(group)
        db.commit()
        db.refresh(group)

        return group

    def list_active(self, db: Session) -> list[RobotGroup]:
        return (
            db.query(RobotGroup)
            .filter(RobotGroup.active.is_(True))
            .order_by(RobotGroup.name)
            .all()
        )

    def get_active_by_id(self, group_id: UUID, db: Session) -> RobotGroup:
        group = (
            db.query(RobotGroup)
            .filter(
                RobotGroup.id == group_id,
                RobotGroup.active.is_(True),
            )
            .first()
        )

        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo não encontrado",
            )

        return group

    def update(
        self,
        group_id: UUID,
        data: RobotGroupUpdate,
        db: Session,
    ) -> RobotGroup:
        group = db.query(RobotGroup).filter(RobotGroup.id == group_id).first()

        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo não encontrado",
            )

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(group, field, value)

        db.commit()
        db.refresh(group)

        return group

    def safe_delete(self, group_id: UUID, db: Session) -> None:
        group = db.query(RobotGroup).filter(RobotGroup.id == group_id).first()

        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo não encontrado",
            )

        group.active = False

        db.query(Robot).filter(Robot.group_id == group_id).update(
            {"group_id": None},
            synchronize_session=False,
        )

        db.commit()

    def list_robots(self, group_id: UUID, db: Session) -> list[Robot]:
        self.get_active_by_id(group_id, db)

        return (
            db.query(Robot)
            .filter(Robot.group_id == group_id)
            .order_by(Robot.name)
            .all()
        )

    def add_robot(
        self,
        group_id: UUID,
        robot_id: UUID,
        db: Session,
    ) -> Robot:
        self.get_active_by_id(group_id, db)

        robot = db.query(Robot).filter(Robot.id == robot_id).first()

        if robot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Robô não encontrado",
            )

        robot.group_id = group_id

        db.commit()
        db.refresh(robot)

        return robot

    def remove_robot(
        self,
        group_id: UUID,
        robot_id: UUID,
        db: Session,
    ) -> Robot:
        robot = (
            db.query(Robot)
            .filter(
                Robot.id == robot_id,
                Robot.group_id == group_id,
            )
            .first()
        )

        if robot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Robô não encontrado neste grupo",
            )

        robot.group_id = None

        db.commit()
        db.refresh(robot)

        return robot