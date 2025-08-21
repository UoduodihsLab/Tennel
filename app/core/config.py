# app/core/config.py
from pathlib import Path
from typing import Tuple

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

    ENABLE_PROXY: bool = True
    PROXY: Tuple[str, str, int, str, str] = ('socks5', '127.0.0.1', 7897, '', '')

    TOKEN_SECRET_KEY: str
    TOKEN_ALGORITHM: str

    MAX_CHANNELS_COUNT_PER_ACCOUNT: int = 10

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
    )


settings = Settings()
