from pathlib import Path
import os
import re
import shutil
import subprocess

from app.settings import settings


class CodeEditorService:
    def __init__(self):
        self.base_path = Path(settings.PROJECTS_BASE_PATH)
        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def find_projects(self):
        result = []

        for item in self.base_path.iterdir():
            if item.is_dir():
                result.append({
                    "name": item.name,
                })

        result.sort(
            key=lambda item: item["name"]
        )

        return result

    def create_project(
        self,
        name: str,
    ):
        sanitized = self._sanitize_project_name(name)

        if not sanitized:
            raise ValueError("Nome do projeto inválido.")

        project_path = self.base_path / sanitized

        if project_path.exists():
            raise ValueError("Projeto já existe.")

        project_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        command = [
            "pio",
            "project",
            "init",
            "--board",
            "esp32dev",
            "--project-option",
            "framework=arduino",
        ]

        result = subprocess.run(
            command,
            cwd=str(project_path),
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            shutil.rmtree(
                project_path,
                ignore_errors=True,
            )

            raise ValueError(
                "Falha ao inicializar projeto PlatformIO: "
                f"{result.stderr or result.stdout}"
            )

        self._create_file(
            project_path / "platformio.ini",
            self._platformio_ini(),
        )

        self._create_file(
            project_path / "partitions.csv",
            self._partitions_csv(),
        )

        self._create_file(
            project_path / "src" / "main.cpp",
            self._main_cpp(),
        )

        self._create_file(
            project_path / "README.md",
            f"# {sanitized}\n",
        )

        return {
            "name": sanitized,
            "path": str(project_path),
        }

    def get_tree(
        self,
        project: str,
    ):
        project_path = self._get_project_path(project)

        result = []

        for root, dirs, files in os.walk(project_path):
            dirs[:] = [
                directory for directory in dirs
                if directory not in [".git", ".pio", ".vscode"]
            ]

            relative_root = os.path.relpath(
                root,
                project_path,
            )

            if relative_root == ".":
                relative_root = ""

            for directory in dirs:
                path = os.path.join(
                    relative_root,
                    directory,
                ).replace("\\", "/")

                result.append({
                    "name": directory,
                    "path": path,
                    "directory": True,
                })

            for file in files:
                path = os.path.join(
                    relative_root,
                    file,
                ).replace("\\", "/")

                result.append({
                    "name": file,
                    "path": path,
                    "directory": False,
                })

        result.sort(
            key=lambda item: (
                item["path"].count("/"),
                not item["directory"],
                item["path"],
            )
        )

        return result

    def read_file(
        self,
        project: str,
        path: str,
    ):
        file_path = self._get_safe_path(
            project=project,
            path=path,
        )

        if not file_path.exists():
            raise ValueError("Arquivo não encontrado.")

        if not file_path.is_file():
            raise ValueError("O caminho informado não é um arquivo.")

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:
            content = file.read()

        return {
            "path": path,
            "content": content,
        }

    def save_file(
        self,
        project: str,
        path: str,
        content: str,
    ):
        file_path = self._get_safe_path(
            project=project,
            path=path,
        )

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(content)

        return {
            "message": "Arquivo salvo.",
            "path": path,
        }

    def create_file(
        self,
        project: str,
        path: str,
        content: str = "",
    ):
        file_path = self._get_safe_path(
            project=project,
            path=path,
        )

        if file_path.exists():
            raise ValueError("Arquivo já existe.")

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(content)

        return {
            "message": "Arquivo criado.",
            "path": path,
        }

    def create_folder(
        self,
        project: str,
        path: str,
    ):
        folder_path = self._get_safe_path(
            project=project,
            path=path,
        )

        if folder_path.exists():
            raise ValueError("Pasta já existe.")

        folder_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return {
            "message": "Pasta criada.",
            "path": path,
        }

    def delete_path(
        self,
        project: str,
        path: str,
    ):
        target = self._get_safe_path(
            project=project,
            path=path,
        )

        if not target.exists():
            raise ValueError("Arquivo ou pasta não encontrado.")

        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()

        return {
            "message": "Removido com sucesso.",
            "path": path,
        }

    def _get_project_path(
        self,
        project: str,
    ) -> Path:
        sanitized = self._sanitize_project_name(project)
        project_path = self.base_path / sanitized

        if not project_path.exists():
            raise ValueError("Projeto não encontrado.")

        if not project_path.is_dir():
            raise ValueError("Projeto inválido.")

        return project_path

    def _get_safe_path(
        self,
        project: str,
        path: str,
    ) -> Path:
        project_path = self._get_project_path(project)

        normalized_path = path.strip().replace("\\", "/").lstrip("/")

        if not normalized_path:
            raise ValueError("Caminho inválido.")

        target = (project_path / normalized_path).resolve()
        project_root = project_path.resolve()

        if not str(target).startswith(str(project_root)):
            raise ValueError("Caminho fora do projeto não permitido.")

        return target

    def _sanitize_project_name(
        self,
        name: str,
    ) -> str:
        return re.sub(
            r"[^a-z0-9_\-]",
            "_",
            name.strip().lower().replace(" ", "_"),
        ).strip("_")

    def _create_file(
        self,
        path: Path,
        content: str,
    ):
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(content.strip() + "\n")

    def _platformio_ini(self):
        return """
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino

monitor_speed = 115200
upload_speed = 921600

board_build.partitions = partitions.csv
"""

    def _main_cpp(self):
        return """
#include <Arduino.h>

#define LED_PIN 2

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(500);

  digitalWrite(LED_PIN, LOW);
  delay(500);
}
"""

    def _partitions_csv(self):
        return """
# Name,   Type, SubType, Offset,   Size,     Flags
nvs,      data, nvs,     0x9000,   0x5000,
otadata,  data, ota,     0xe000,   0x2000,
factory,  app,  factory, 0x10000,  0x140000,
ota_0,    app,  ota_0,   0x150000, 0x140000,
ota_1,    app,  ota_1,   0x290000, 0x140000,
spiffs,   data, spiffs,  0x3D0000, 0x30000,
"""