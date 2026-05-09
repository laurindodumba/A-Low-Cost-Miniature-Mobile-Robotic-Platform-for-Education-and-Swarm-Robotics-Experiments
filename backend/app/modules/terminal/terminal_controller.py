import subprocess

from fastapi import APIRouter, HTTPException

from app.modules.terminal.terminal_schema import (
    TerminalCommandRequest,
    TerminalCommandResponse,
)
from app.modules.terminal.terminal_service import TerminalService

router = APIRouter(
    prefix="/api/terminal",
    tags=["Terminal"],
)

service = TerminalService()


@router.post("/execute", response_model=TerminalCommandResponse)
def execute_command(request: TerminalCommandRequest):
    try:
        return service.execute(request)

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail="Tempo limite do comando excedido.",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar comando: {error}",
        )