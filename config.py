from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterable

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    composio_api_key: str = field(default_factory=lambda: os.getenv("COMPOSIO_API_KEY", ""))
    composio_user_id: str = field(default_factory=lambda: os.getenv("COMPOSIO_USER_ID", "user-123"))
    github_owner: str = field(default_factory=lambda: os.getenv("GITHUB_OWNER", "innocentaluma11-rgb"))
    github_repo: str = field(default_factory=lambda: os.getenv("GITHUB_REPO", "TABERBNACLEFX-"))
    mt5_login: int | None = field(default_factory=lambda: _int_env("MT5_LOGIN"))
    mt5_server: str | None = field(default_factory=lambda: os.getenv("MT5_SERVER"))
    mt5_password: str | None = field(default_factory=lambda: os.getenv("MT5_PASSWORD"))
    mt5_terminal_path: str | None = field(default_factory=lambda: os.getenv("MT5_TERMINAL_PATH"))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    allowed_symbols: tuple[str, ...] = field(default_factory=lambda: _split_csv("ALLOWED_SYMBOLS", default="EURUSD,GBPUSD,USDJPY,XAUUSD"))
    max_daily_loss: float = field(default_factory=lambda: float(os.getenv("MAX_DAILY_LOSS", "250.0")))
    max_position_size: float = field(default_factory=lambda: float(os.getenv("MAX_POSITION_SIZE", "0.10")))
    min_confidence: float = field(default_factory=lambda: float(os.getenv("MIN_CONFIDENCE", "0.6")))
    default_platform: str = field(default_factory=lambda: os.getenv("DEFAULT_SOCIAL_PLATFORM", "instagram"))
    social_platforms: tuple[str, ...] = field(default_factory=lambda: _split_csv("SOCIAL_PLATFORMS", default="instagram,tiktok,youtube"))
    env_mode: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))

    @property
    def is_safe_mode(self) -> bool:
        return self.env_mode.lower() != "production"

    def platform_toolkit(self, platform: str) -> str:
        env_key = f"COMPOSIO_{platform.upper()}_TOOLKIT"
        value = os.getenv(env_key, platform.lower())
        return value.strip().lower()

    def publish_tool_slug(self, platform: str) -> str:
        env_key = f"COMPOSIO_{platform.upper()}_PUBLISH_TOOL"
        return os.getenv(env_key, "").strip()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.composio_api_key:
            errors.append("COMPOSIO_API_KEY is required")
        if not self.composio_user_id:
            errors.append("COMPOSIO_USER_ID is required")
        if not self.allowed_symbols:
            errors.append("ALLOWED_SYMBOLS cannot be empty")
        return errors


def _split_csv(value: str, default: str) -> tuple[str, ...]:
    raw = os.getenv(value, default)
    return tuple(part.strip().lower() for part in raw.split(",") if part.strip())


def _int_env(name: str) -> int | None:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


def get_settings() -> Settings:
    return Settings()
