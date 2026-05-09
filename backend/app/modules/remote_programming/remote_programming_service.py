from sqlalchemy.orm import Session

from app.modules.robot.robot_model import Robot
from app.modules.robot_group.robot_group_model import RobotGroup
from app.modules.programming_file_upload.programming_file_model import ProgrammingFile


class RemoteProgrammingService:

    def send(self, db: Session, request):
        program = db.query(ProgrammingFile).filter(
            ProgrammingFile.id == request.program_id
        ).first()

        if not program:
            raise ValueError("Programa não encontrado.")

        robots = []

        if request.robot_id:
            robot = db.query(Robot).filter(
                Robot.id == request.robot_id
            ).first()

            if not robot:
                raise ValueError("Robô não encontrado.")

            robots.append(robot)

        elif request.group_id:
            group = db.query(RobotGroup).filter(
                RobotGroup.id == request.group_id
            ).first()

            if not group:
                raise ValueError("Grupo não encontrado.")

            robots = group.robots

        else:
            raise ValueError("Informe robô ou grupo.")

        for robot in robots:
            print(f"Enviando {program.name} para {robot.name}")

        return {
            "status": "SUCCESS",
            "message": f"Programa enviado para {len(robots)} robô(s)"
        }