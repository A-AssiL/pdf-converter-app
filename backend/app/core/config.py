"""Application configuration settings and environment values."""

from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    redis_url: str = "redis://redis:6379/0"
    result_backend: str = "redis://redis:6379/1"
    database_url: str = "sqlite:///./backend/app/db/app.db"
    upload_dir: Path = BASE_DIR / "storage" / "uploads"
    processed_dir: Path = BASE_DIR / "storage" / "processed"
    temp_dir: Path = BASE_DIR / "storage" / "temp"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"