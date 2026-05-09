import base64
from binascii import Error as Base64Error

from sqlalchemy.orm import Session

from app.modules.programming_file_upload.programming_file_model import ProgrammingFile
from app.modules.programming_file_upload.programming_file_schema import ProgrammingFileCreateRequest


class ProgrammingFileService:
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def create(
        self,
        db: Session,
        request: ProgrammingFileCreateRequest,
    ) -> ProgrammingFile:
        file_data = self._decode_file(request.file_base64)

        if len(file_data) != request.file_size:
            raise ValueError("Tamanho do arquivo inválido.")

        if len(file_data) > self.MAX_FILE_SIZE:
            raise ValueError("Arquivo excede o tamanho máximo permitido.")

        entity = ProgrammingFile(
            name=request.name,
            description=request.description,
            file_name=request.file_name,
            content_type=request.content_type,
            file_size=len(file_data),
            file_data=file_data,
            active=True,
        )

        db.add(entity)
        db.commit()
        db.refresh(entity)

        return entity

    def _decode_file(self, file_base64: str) -> bytes:
        try:
            return base64.b64decode(file_base64, validate=True)
        except Base64Error:
            raise ValueError("Arquivo base64 inválido.")