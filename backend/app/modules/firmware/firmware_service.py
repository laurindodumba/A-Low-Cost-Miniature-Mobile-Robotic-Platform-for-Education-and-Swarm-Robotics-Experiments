import asyncio
import base64
import os
import tempfile
from binascii import Error as Base64Error

from sqlalchemy.orm import Session

from app.settings import settings
from app.modules.firmware.firmware_model import FirmwareFile
from app.modules.firmware.firmware_schema import (
    FirmwareBinaryRequest,
    FirmwareCreateRequest,
)


class FirmwareService:
    MAX_TOTAL_SIZE = 20 * 1024 * 1024

    BOOTLOADER_OFFSET = "0x1000"
    PARTITIONS_OFFSET = "0x8000"
    FIRMWARE_OFFSET = "0x10000"

    def create(
        self,
        db: Session,
        request: FirmwareCreateRequest,
    ) -> FirmwareFile:
        bootloader_data = self._decode_and_validate(
            file=request.bootloader,
            expected_name="bootloader.bin",
        )

        partitions_data = self._decode_and_validate(
            file=request.partitions,
            expected_name="partitions.bin",
        )

        firmware_data = self._decode_and_validate(
            file=request.firmware,
            expected_name="firmware.bin",
        )

        total_size = (
            len(bootloader_data)
            + len(partitions_data)
            + len(firmware_data)
        )

        if total_size > self.MAX_TOTAL_SIZE:
            raise ValueError("Pacote de firmware excede o tamanho máximo permitido.")

        entity = FirmwareFile(
            name=request.name,
            description=request.description,

            bootloader_file_name=request.bootloader.file_name,
            bootloader_file_data=bootloader_data,
            bootloader_file_size=len(bootloader_data),

            partitions_file_name=request.partitions.file_name,
            partitions_file_data=partitions_data,
            partitions_file_size=len(partitions_data),

            firmware_file_name=request.firmware.file_name,
            firmware_file_data=firmware_data,
            firmware_file_size=len(firmware_data),

            total_size=total_size,
            active=True,
        )

        db.add(entity)
        db.commit()
        db.refresh(entity)

        return entity

    def find_all(self, db: Session) -> list[FirmwareFile]:
        return (
            db.query(FirmwareFile)
            .filter(FirmwareFile.active.is_(True))
            .order_by(FirmwareFile.created_at.desc())
            .all()
        )

    async def flash_firmware_via_cable(
        self,
        db: Session,
        robot_id: str,
        firmware_id: str,
    ):
        firmware = self._find_firmware(db, firmware_id)
        temp_files: list[str] = []

        try:
            yield "[INFO] Gravação do boot/base iniciada."
            yield "[INFO] Robô selecionado ignorado temporariamente."
            yield f"[INFO] Porta serial: {settings.ESP32_SERIAL_PORT}"
            yield f"[INFO] Baudrate: {settings.ESP32_UPLOAD_BAUDRATE}"
            yield "[INFO] Arquivos:"
            yield f"[INFO] - {firmware.bootloader_file_name} -> {self.BOOTLOADER_OFFSET}"
            yield f"[INFO] - {firmware.partitions_file_name} -> {self.PARTITIONS_OFFSET}"
            yield f"[INFO] - {firmware.firmware_file_name} -> {self.FIRMWARE_OFFSET}"

            bootloader_path = self._create_temp_file(
                file_data=firmware.bootloader_file_data,
                file_name="bootloader.bin",
            )

            partitions_path = self._create_temp_file(
                file_data=firmware.partitions_file_data,
                file_name="partitions.bin",
            )

            firmware_path = self._create_temp_file(
                file_data=firmware.firmware_file_data,
                file_name="firmware.bin",
            )

            temp_files.extend([
                bootloader_path,
                partitions_path,
                firmware_path,
            ])

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

                self.BOOTLOADER_OFFSET,
                bootloader_path,

                self.PARTITIONS_OFFSET,
                partitions_path,

                self.FIRMWARE_OFFSET,
                firmware_path,
            ]

            yield "[INFO] Executando esptool..."

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

                    message = line.decode(errors="ignore").strip()

                    if message:
                        yield message

            exit_code = await process.wait()

            if exit_code == 0:
                yield "[DONE] Firmware base gravado com sucesso."
            else:
                yield f"[ERROR] Falha ao gravar firmware base. Código: {exit_code}"

        except Exception as error:
            yield f"[ERROR] {error}"

        finally:
            for path in temp_files:
                self._remove_temp_file(path)

    def _find_firmware(
        self,
        db: Session,
        firmware_id: str,
    ) -> FirmwareFile:
        firmware = (
            db.query(FirmwareFile)
            .filter(
                FirmwareFile.id == firmware_id,
                FirmwareFile.active.is_(True),
            )
            .first()
        )

        if firmware is None:
            raise ValueError("Firmware não encontrado.")

        return firmware

    def _decode_and_validate(
        self,
        file: FirmwareBinaryRequest,
        expected_name: str,
    ) -> bytes:
        if file.file_name != expected_name:
            raise ValueError(f"Arquivo inválido. Esperado: {expected_name}")

        data = self._decode_file(file.file_base64)

        if len(data) != file.file_size:
            raise ValueError(f"Tamanho inválido para {expected_name}.")

        if not file.file_name.lower().endswith(".bin"):
            raise ValueError(f"{expected_name} deve ser um arquivo .bin.")

        return data

    def _decode_file(self, file_base64: str) -> bytes:
        try:
            return base64.b64decode(file_base64, validate=True)
        except Base64Error:
            raise ValueError("Arquivo base64 inválido.")

    def _create_temp_file(
        self,
        file_data: bytes,
        file_name: str,
    ) -> str:
        temp_dir = tempfile.mkdtemp(prefix="robot_firmware_")
        path = os.path.join(temp_dir, file_name)

        with open(path, "wb") as file:
            file.write(file_data)

        return path

    def _remove_temp_file(self, path: str | None) -> None:
        if not path:
            return

        if os.path.exists(path):
            os.remove(path)

        directory = os.path.dirname(path)

        if os.path.exists(directory) and not os.listdir(directory):
            os.rmdir(directory)