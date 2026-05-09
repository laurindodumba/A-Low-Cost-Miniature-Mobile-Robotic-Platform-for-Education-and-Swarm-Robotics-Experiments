from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    ESP32_SERIAL_PORT: str = "/dev/ttyUSB0"
    ESP32_UPLOAD_BAUDRATE: int = 921600

    ESP32_BOOTLOADER_OFFSET: str = "0x1000"
    ESP32_PARTITIONS_OFFSET: str = "0x8000"
    ESP32_FACTORY_OFFSET: str = "0x10000"
    ESP32_PROGRAM_OFFSET: str = "0x150000"

    PROJECTS_BASE_PATH: str = "projetos"

    class Config:
        env_file = ".env"


settings = Settings()