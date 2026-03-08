from functools import lru_cache
import json
from typing import Annotated, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "AI Product Intelligence Platform"
    api_prefix: str = "/api/v1"
    environment: str = "development"

    database_url: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/product_intelligence"
    redis_url: str = "redis://redis:6379/0"

    chroma_host: Optional[str] = None
    chroma_port: int = 8000
    chroma_collection_name: str = "feedback_embeddings"
    chroma_persist_dir: str = "/app/chroma"

    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    llm_provider: str = "openai"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 60 * 24

    cors_origins: Annotated[List[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:80"]
    )
    rate_limit_per_minute: str = "120/minute"

    worker_queue: str = "feedback-jobs"
    feedback_event_channel: str = "feedback_events"

    weekly_report_day: str = "mon"
    weekly_report_hour: int = 8
    weekly_report_minute: int = 0

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
