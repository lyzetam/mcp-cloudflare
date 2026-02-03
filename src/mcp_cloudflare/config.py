"""Pydantic Settings configuration for mcp-cloudflare."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cloudflare configuration from environment variables or .env file.

    All fields map to CLOUDFLARE_<FIELD_NAME> environment variables.
    """

    api_token: str = Field(default="", description="Cloudflare API token")
    account_id: str = Field(default="", description="Cloudflare account ID")

    model_config = SettingsConfigDict(
        env_prefix="CLOUDFLARE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Get configuration from environment variables or .env file."""
    return Settings()
