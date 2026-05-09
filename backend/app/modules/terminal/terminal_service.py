import os
import subprocess

from app.modules.terminal.terminal_schema import (
    TerminalCommandRequest,
    TerminalCommandResponse,
)


class TerminalService:
    TIMEOUT_SECONDS = 15

    def __init__(self):
        self.base_dir = os.getcwd()

    def execute(self, request: TerminalCommandRequest) -> TerminalCommandResponse:
        command = request.command.strip()
        cwd = self._resolve_cwd(request.cwd)

        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=self.TIMEOUT_SECONDS,
        )

        return TerminalCommandResponse(
            command=command,
            cwd=cwd,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )

    def _resolve_cwd(self, cwd: str | None) -> str:
        if not cwd:
            return self.base_dir

        resolved = os.path.abspath(cwd)

        if not os.path.isdir(resolved):
            raise ValueError(f"Diretório não encontrado: {resolved}")

        return resolved