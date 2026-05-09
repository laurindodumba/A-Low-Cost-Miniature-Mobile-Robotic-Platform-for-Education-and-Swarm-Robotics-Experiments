from uuid import UUID
import serial
import json
import time

from sqlalchemy.orm import Session

from app.modules.controllers.robot_control_schema import (
    RobotControlCommandRequest,
    RobotControlCommandResponse,
)


class RobotControlService:

    def send_command(
        self,
        db: Session,
        robot_id: UUID,
        command: RobotControlCommandRequest,
    ) -> RobotControlCommandResponse:

        try:
            ser = serial.Serial(
                port=self._detect_port(),
                baudrate=115200,
                timeout=1,
            )

            time.sleep(2)  # ESP32 reset delay

            payload = {
                "left_x": command.left_x,
                "left_y": command.left_y,
                "right_x": command.right_x,
                "right_y": command.right_y,
            }

            message = json.dumps(payload) + "\n"

            ser.write(message.encode())
            ser.close()

        except Exception as e:
            raise ValueError(f"Erro ao enviar comando: {e}")

        return RobotControlCommandResponse(
            robot_id="ESP32_LOCAL",
            received=True,
            left_x=command.left_x,
            left_y=command.left_y,
            right_x=command.right_x,
            right_y=command.right_y,
        )

    def _detect_port(self):
        import serial.tools.list_ports

        ports = serial.tools.list_ports.comports()

        for port in ports:
            if "USB" in port.device or "ttyUSB" in port.device or "ttyACM" in port.device:
                return port.device

        raise Exception("Nenhum ESP32 encontrado.")