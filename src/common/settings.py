"""Application settings via pydantic-settings."""

from __future__ import annotations

import logging
from functools import lru_cache

from pydantic import AliasChoices
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # AWS
    aws_profile: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AWS_PROFILE", "AWS_DEFAULT_PROFILE"),
    )
    aws_region: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AWS_REGION", "AWS_DEFAULT_REGION"),
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://appuser:localdev@localhost:5432/appdb",
        validation_alias="DATABASE_URL",
    )

    # Bedrock
    bedrock_model_id: str = Field(
        default="us.anthropic.claude-sonnet-4-20250514",
        validation_alias="BEDROCK_MODEL_ID",
    )
    bedrock_embedding_model_id: str = Field(
        default="amazon.titan-embed-text-v2:0",
        validation_alias="BEDROCK_EMBEDDING_MODEL_ID",
    )

    # Logging
    logging_config_path: str = Field(
        default="config/logging.ini",
        validation_alias="LOGGING_CONFIG_PATH",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()  # type: ignore[call-arg]
