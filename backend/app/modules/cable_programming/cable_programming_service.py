import asyncio
import json
import os
import tempfile
from uuid import UUID

from sqlalchemy.orm import Session

from app.settings import settings
from app.modules.programming_file_upload.programming_file_model import ProgrammingFile
from app.modules.robot.robot_model import Robot


class CableProgrammingService:
    def find_robot(
        self,
        db: Session,
        robot_id: UUID,
    ) -> Robot:
        robot = (
            db.query(Robot)
            .filter(
                Robot.id == robot_id,
                Robot.active.is_(True),
            )
            .first()
        )

        if robot is None:
            raise ValueError("Robô não encontrado.")

        return robot

    def find_program(
        self,
        db: Session,
        program_id: UUID,
    ) -> ProgrammingFile:
        program = (
            db.query(ProgrammingFile)
            .filter(
                ProgrammingFile.id == program_id,
                ProgrammingFile.active.is_(True),
            )
            .first()
        )

        if program is None:
            raise ValueError("Programa não encontrado.")

        return program

    async def stream_flash_logs(
        self,
        db: Session,
        robot_id: UUID,
        program_id: UUID,
    ):
        program_path = None

        try:
            robot = self.find_robot(
                db=db,
                robot_id=robot_id,
            )

            program = self.find_program(
                db=db,
                program_id=program_id,
            )

            yield self._log(
                "Iniciando gravação do programa do robô..."
            )

            yield self._log(
                f"Robô selecionado: {robot.name}"
            )

            yield self._log(
                f"Programa selecionado: {program.name}"
            )

            yield self._log(
                f"Arquivo: {program.file_name}"
            )

            yield self._log(
                f"Porta serial: {settings.ESP32_SERIAL_PORT}"
            )

            yield self._log(
                f"Baudrate: {settings.ESP32_UPLOAD_BAUDRATE}"
            )

            yield self._log(
                f"Offset OTA: {settings.ESP32_PROGRAM_OFFSET}"
            )

            yield self._log(
                "Gerando arquivo temporário..."
            )

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".bin",
            ) as temp_file:
                temp_file.write(program.file_data)
                program_path = temp_file.name

            yield self._log(
                f"Arquivo temporário criado: {program_path}"
            )

            command = [
                "python3",
                "-m",
                "esptool",
                "--chip",
                "esp32",
                "--port",
                settings.ESP32_SERIAL_PORT,
                "--baud",
                str(settings.ESP32_UPLOAD_BAUDRATE),
                "write-flash",
                settings.ESP32_PROGRAM_OFFSET,
                program_path,
            ]

            yield self._log(
                "Executando esptool..."
            )

            yield self._log(
                " ".join(command)
            )

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )

            if process.stdout is None:
                yield self._log(
                    "[ERROR] Não foi possível ler saída do processo."
                )
                return

            while True:
                line = await process.stdout.readline()

                if not line:
                    break

                message = line.decode(
                    errors="ignore"
                ).rstrip()

                if message:
                    yield self._log(message)

            exit_code = await process.wait()

            if exit_code == 0:
                yield self._log(
                    "[DONE] Programa gravado com sucesso em ota_0."
                )
            else:
                yield self._log(
                    f"[ERROR] Falha ao gravar programa. Código: {exit_code}"
                )

        except Exception as error:
            yield self._log(
                f"[ERROR] {error}"
            )

        finally:
            if (
                program_path and
                os.path.exists(program_path)
            ):
                os.remove(program_path)

    def _log(
        self,
        message: str,
    ) -> str:
        return json.dumps(
            {
                "type": "log",
                "message": message,
            }
        )