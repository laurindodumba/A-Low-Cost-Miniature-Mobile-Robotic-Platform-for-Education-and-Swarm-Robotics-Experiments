from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_tables

from app.modules.robot import robot_model
from app.modules.robot.robot_controller import router as robot_router
from app.modules.robot.robot_network_controller import router as robot_network_router

from app.modules.robot_group import robot_group_model
from app.modules.robot_group.robot_group_controller import router as robot_group_router

from app.modules.controllers.robot_control_controller import router as robot_control_router
from app.modules.terminal.terminal_controller import router as terminal_router

from app.modules.programming_file_upload.programming_file_controller import (
    router as programming_file_router,
)

from app.modules.cable_programming.cable_programming_controller import (
    router as cable_programming_router,
)

from app.modules.remote_programming.remote_programming_controller import (
    router as remote_programming_router)
from app.modules.remote_programming.ota_controller import (
    router as ota_route)

from app.modules.firmware.firmware_controller import (
    router as firmware_router)

from app.modules.code_compile.code_editor_controller import router as code_editor_router
from app.modules.code_compile.code_compile_controller import router as code_compile_router





app = FastAPI(
    title="Robot Manager API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    create_tables()

    print("\nROTAS REGISTRADAS:")
    for route in app.routes:
        print(route.path, getattr(route, "methods", "WEBSOCKET"))


app.include_router(robot_router)
app.include_router(robot_network_router)
app.include_router(robot_group_router)
app.include_router(robot_control_router)
app.include_router(terminal_router)
app.include_router(programming_file_router)
app.include_router(cable_programming_router)
app.include_router(remote_programming_router)
app.include_router(ota_route)
app.include_router(firmware_router)
app.include_router(code_editor_router)
app.include_router(code_compile_router)



@app.get("/")
def root():
    return {
        "status": "ok",
        "app": "robot-manager",
        "version": "1.0.0",
        "message": "API rodando 🚀",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": "robot-manager",
        "version": "1.0.0",
    }