from functools import lru_cache
from pathlib import Path

import os

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_database_url() -> str:
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit
    if os.getenv("VERCEL"):
        return "sqlite:////tmp/reviews.db"
    return "sqlite:///./data/reviews.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    database_url: str = Field(default_factory=_default_database_url)
    source_config_path: str = "./config/source_config.yaml"


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_source_config() -> dict:
    settings = get_settings()
    path = Path(settings.source_config_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[1] / path
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)
