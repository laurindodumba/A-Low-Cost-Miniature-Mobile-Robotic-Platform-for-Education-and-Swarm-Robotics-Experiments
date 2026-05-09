import asyncio
import os
import tempfile
from pathlib import Path

from sqlalchemy.orm import Session

from app.settings import settings
from app.modules.programming_file_upload.programming_file_model import ProgrammingFile


class CodeCompileService:
    BUILD_PATH = ".pio/build/esp32dev/firmware.bin"

    def __init__(self):
        self.projects_path = Path(settings.PROJECTS_BASE_PATH)

    async def compile_project(
        self,
        db: Session,
        project: str,
    ):
        async for log in self._compile_and_save(db=db, project=project):
            yield log

    async def compile_and_run_project(
        self,
        db: Session,
        project: str,
    ):
        firmware_data = None

        async for result in self._compile_and_save(
            db=db,
            project=project,
            return_firmware=True,
        ):
            if isinstance(result, bytes):
                firmware_data = result
                continue

            yield result

        if firmware_data is None:
            yield "[ERROR] Firmware não disponível para gravação."
            return

        async for log in self._flash_program(firmware_data):
            yield log

    async def _compile_and_save(
        self,
        db: Session,
        project: str,
        return_firmware: bool = False,
    ):
        project_path = self.projects_path / project

        if not project_path.exists():
            yield "[ERROR] Projeto não encontrado."
            return

        if not (project_path / "platformio.ini").exists():
            yield "[ERROR] platformio.ini não encontrado."
            return

        yield f"[INFO] Projeto: {project}"
        yield f"[INFO] Caminho: {project_path}"
        yield "[INFO] Iniciando compilação com PlatformIO..."

        command = ["pio", "run"]

        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=str(project_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        if process.stdout is not None:
            while True:
                line = await process.stdout.readline()

                if not line:
                    break

                message = line.decode(errors="ignore").rstrip()

                if message:
                    yield message

        exit_code = await process.wait()

        if exit_code != 0:
            yield f"[ERROR] Falha na compilação. Código: {exit_code}"
            return

        firmware_path = project_path / self.BUILD_PATH

        if not firmware_path.exists():
            yield "[ERROR] firmware.bin não encontrado após compilação."
            return

        yield "[INFO] firmware.bin gerado com sucesso."

        with open(firmware_path, "rb") as file:
            firmware_data = file.read()

        program = ProgrammingFile(
            name=project,
            description=f"Build automático do projeto {project}",
            file_name="firmware.bin",
            content_type="application/octet-stream",
            file_size=len(firmware_data),
            file_data=firmware_data,
            active=True,
        )

        db.add(program)
        db.commit()
        db.refresh(program)

        yield f"[DONE] Programa salvo com sucesso. ID: {program.id}"

        if return_firmware:
            yield firmware_data

    async def _flash_program(self, firmware_data: bytes):
        temp_path = None

        try:
            yield "[INFO] Preparando gravação no ESP32..."

            with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as temp_file:
                temp_file.write(firmware_data)
                temp_path = temp_file.name

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
                temp_path,
            ]

            yield f"[INFO] Porta serial: {settings.ESP32_SERIAL_PORT}"
            yield f"[INFO] Offset programa: {settings.ESP32_PROGRAM_OFFSET}"
            yield "[INFO] Gravando programa no robô..."

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )

            if process.stdout is not None:
                while True:
                    line = await process.stdout.readline()

                    if not line:
                        break

                    message = line.decode(errors="ignore").rstrip()

                    if message:
                        yield message

            exit_code = await process.wait()

            if exit_code == 0:
                yield "[DONE] Programa compilado e gravado com sucesso."
            else:
                yield f"[ERROR] Falha ao gravar programa. Código: {exit_code}"

        except Exception as error:
            yield f"[ERROR] {error}"

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)