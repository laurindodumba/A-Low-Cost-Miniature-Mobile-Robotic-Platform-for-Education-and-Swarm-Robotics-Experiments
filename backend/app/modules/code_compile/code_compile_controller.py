import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.database import SessionLocal
from app.modules.code_compile.code_compile_service import CodeCompileService

router = APIRouter(
    prefix="/api/code",
    tags=["Code Compile"],
)

service = CodeCompileService()


@router.websocket("/compile/ws/{project}")
async def compile_project_ws(websocket: WebSocket, project: str):
    await websocket.accept()
    db = SessionLocal()

    try:
        async for log in service.compile_project(db=db, project=project):
            await websocket.send_text(json.dumps({"message": log}))
    except WebSocketDisconnect:
        pass
    finally:
        db.close()
        try:
            await websocket.close()
        except RuntimeError:
            pass


@router.websocket("/compile-and-run/ws/{project}")
async def compile_and_run_project_ws(websocket: WebSocket, project: str):
    await websocket.accept()
    db = SessionLocal()

    try:
        async for log in service.compile_and_run_project(db=db, project=project):
            await websocket.send_text(json.dumps({"message": log}))
    except WebSocketDisconnect:
        pass
    finally:
        db.close()
        try:
            await websocket.close()
        except RuntimeError:
            pass