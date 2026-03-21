"""Application configuration using Pydantic Settings."""

import os
from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    url: str = Field(
        default=os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/mobile_dev_platform"),
        description="Async PostgreSQL database URL",
    )
    echo: bool = Field(default=False, description="Echo SQL queries")
    pool_size: int = Field(default=20, ge=1, description="Connection pool size")
    max_overflow: int = Field(default=10, ge=0, description="Max overflow connections")
    pool_timeout: int = Field(default=30, ge=1, description="Pool timeout in seconds")
    pool_recycle: int = Field(default=3600, ge=0, description="Pool recycle in seconds")


class JWTSettings(BaseSettings):
    """JWT configuration."""

    secret_key: str = Field(default="dev-secret-key", description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, ge=1, description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, ge=1, description="Refresh token expiration in days"
    )


class RedisSettings(BaseSettings):
    """Redis configuration."""

    url: str = Field(
        default=os.getenv("REDIS_URL", "redis://localhost:6379/0"), description="Redis URL"
    )


class ClaudeAPISettings(BaseSettings):
    """Claude API configuration."""

    api_key: str = Field(
        default=os.getenv("ANTHROPIC_API_KEY", ""),
        description="Anthropic Claude API key",
    )
    api_url: str = Field(
        default=os.getenv("ANTHROPIC_API_URL", "https://api.anthropic.com"),
        description="Anthropic Claude API URL",
    )
    max_retries: int = Field(default=3, ge=0, description="Max retry attempts")
    timeout: int = Field(default=60, ge=1, description="Request timeout in seconds")


class APIKeySettings(BaseSettings):
    """API Key management configuration."""

    encryption_key: str = Field(
        default=os.getenv("API_KEY_ENCRYPTION_KEY", "dev-encryption-key-change-in-production"),
        description="Encryption key for API keys",
    )
    default_rate_limit: int = Field(default=100, ge=1, description="Default rate limit per window")
    default_rate_limit_window: int = Field(default=60, ge=1, description="Rate limit window in seconds")
    max_keys_per_user: int = Field(default=10, ge=1, description="Max API keys per user")
    max_keys_per_project: int = Field(default=5, ge=1, description="Max API keys per project")


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = Field(
        default="Mobile Development Platform",
        description="Application name",
    )
    debug: bool = Field(default=False, description="Debug mode")
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    claude_api: ClaudeAPISettings = Field(default_factory=ClaudeAPISettings)
    api_key: APIKeySettings = Field(default_factory=APIKeySettings)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
