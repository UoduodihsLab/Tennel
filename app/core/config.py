# app/core/config.py

from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    BASE_DIR: Path = BASE_DIR

    LOG_LEVEL: str = 'INFO'

    DATABASE_URL: PostgresDsn

    @property
    def db_url(self) -> str:
        return str(self.DATABASE_URL)

    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str

    TOKEN_SECRET_KEY: str
    TOKEN_ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
    )


settings = Settings()
