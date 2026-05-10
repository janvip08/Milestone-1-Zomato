"""Configuration placeholders for Phase 0."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    """Minimal configuration container."""

    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")


def get_config() -> AppConfig:
    """Return application configuration."""
    return AppConfig()

