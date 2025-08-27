# app/core/config.py
from pathlib import Path
from typing import Tuple, List

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    BASE_DIR: Path = BASE_DIR

    TELEGRAM_SESSIONS_ROOT: Path = BASE_DIR / "sessions"

    LOG_LEVEL: str = 'INFO'

    DATABASE_URL: PostgresDsn

    @property
    def db_url(self) -> str:
        return str(self.DATABASE_URL)

    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str

    ENABLE_PROXY: bool
    PROXY: Tuple[str, str, int, str, str]

    TOKEN_SECRET_KEY: str
    TOKEN_ALGORITHM: str

    MAX_CHANNELS_COUNT_PER_ACCOUNT: int = 10

    MEDIA_ROOT: Path = BASE_DIR / 'media'
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", 'image/jpg']
    ALLOWED_VIDEO_TYPES: List[str] = ['video/mp4']
    VIDEO_MAX_SIZE: int = 100 * 1024 * 1024
    IMG_MAX_SIZE: int = 15 * 1024 * 1024

    TASK_INTERVAL_TIME: int = 5

    AI_API_KEY: str
    AI_API_URL: str

    DEBUG: bool

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
    )


settings = Settings()
