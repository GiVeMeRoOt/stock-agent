"""Application configuration using Pydantic settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Central application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["dev", "prod", "test"] = Field(
        default="dev", validation_alias="ENVIRONMENT"
    )
    db_url: str = Field(
        default="sqlite+aiosqlite:///./data/dsp.db",
        validation_alias="DB_URL",
    )
    data_dir: Path = Field(default=Path("./data"), validation_alias="DATA_DIR")
    timezone: str = Field(default="Asia/Kolkata", validation_alias="TZ")
    scraper_request_interval: float = Field(
        default=1.0, validation_alias="SCRAPER_REQUEST_INTERVAL"
    )
    scraper_max_retries: int = Field(
        default=5, validation_alias="SCRAPER_MAX_RETRIES"
    )
    scheduler_daily_time: str = Field(
        default="08:30", validation_alias="SCHEDULER_DAILY_TIME"
    )

@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return a cached settings instance."""

    settings = AppSettings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
