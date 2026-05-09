from typing import Optional

from pydantic import BaseModel, Field


class TerminalCommandRequest(BaseModel):
    command: str = Field(min_length=1, max_length=500)
    cwd: Optional[str] = None


class TerminalCommandResponse(BaseModel):
    command: str
    cwd: str
    stdout: str
    stderr: str
    exit_code: int