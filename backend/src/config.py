"""
Centralised configuration module for the AI Legal Document Assistant.
All environment values are accessed through the Settings class
so no file ever reads os.environ directly.
"""

import os
from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = [
    "APP_ENV",
    "APP_PORT",
]


def validate_env():
    """Validate that all critical environment variables are present."""
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables:\n  " + "\n  ".join(missing)
        )


class Settings:
    """Single source of truth for all configuration values."""

    # Application
    ENV: str = os.getenv("APP_ENV", "development")
    PORT: int = int(os.getenv("APP_PORT", "8000"))
    HOST: str = os.getenv("APP_HOST", "0.0.0.0")


# Validate on import
validate_env()

settings = Settings()

