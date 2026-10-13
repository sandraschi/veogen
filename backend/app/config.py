from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment variables (.env by default).

    Industrial v3.1 SOTA Integration:
    - Gemini 3.1 Pro/Flash/TTS
    - Veo 3.1 (Video)
    - Lyria 3 (Music)
    - Nano Banana 2 (Imagen 3 / Flash Image)
    """

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=(".env", "../.env"),  # backend/.env first, repo-root .env fallback
        case_sensitive=True,
    )

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "VeoGen Industrial"
    VERSION: str = "3.1.0"
    DESCRIPTION: str = (
        "SOTA 2026 AI Video & Media Generation Platform.\n\nFeaturing Gemini 3.1, Veo 3.1, Lyria 3, and Nano Banana 2."
    )

    # Server Configuration (Fleet Standard)
    # Phase 2 salvage: moved off 10730/10731 (10730 belongs to moltbot-mcp).
    # Registered pair 11150/11151 + metrics 11152 in WEBAPP_PORTS.md.
    HOST: str = "0.0.0.0"
    PORT: int = 11150
    FRONTEND_PORT: int = 11151
    DEBUG: bool = False
    WORKERS: int = 1

    # Google Cloud Configuration
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GOOGLE_API_KEY: Optional[str] = None

    # Gemini 3.1 Configuration
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_PRO_MODEL: str = "gemini-3.1-pro"
    GEMINI_FLASH_MODEL: str = "gemini-3.1-flash"
    GEMINI_TTS_MODEL: str = "gemini-3.1-flash-tts-preview"

    # Veo 3.1 Configuration (Video)
    VEO_MODEL: str = "veo-3.1"
    VEO_MAX_DURATION: int = 60

    # Lyria 3 Configuration (Music)
    LYRIA_MODEL: str = "lyria-3-pro-preview"

    # Imagen 3 Configuration (Nano Banana 2 / Flash Image)
    IMAGEN_MODEL: str = "gemini-3.1-flash-image-preview"

    # File Storage
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    TEMP_DIR: str = "temp"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB

    # Database Configuration - local SQLite by default (single-user fleet
    # deployment). Override DATABASE_URL for Postgres.
    DATABASE_URL: Optional[str] = "sqlite:///./veogen.db"

    # Security - MUST be overridden via .env in any shared deployment.
    SECRET_KEY: str = "change-me-in-env"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # CORS (Standardized for Fleet)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:11151",
        "http://127.0.0.1:11151",
        "http://localhost:11150",
        "http://127.0.0.1:11150",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "veogen.log"

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 11152

    # Email Configuration (Legacy support)
    EMAIL_FROM: str = "noreply@veogen.local"
    EMAIL_SMTP: str = "dev"
    EMAIL_DEV_OUTBOX: str = "dev_emails/"

    # Feature flags consumed by services (Phase 2 salvage: fields the
    # endpoint layer reads but the v3.1 rewrite forgot to declare)
    FLOW_ENABLED: bool = False
    FLOW_API_BASE_URL: str = "http://localhost:3000"
    FLOW_DEFAULT_REGION: str = "eu-central-1"
    FLOW_WEBHOOK_SECRET: str = "change-me"
    AUDIOFX_ENABLED: bool = False
    AUDIOFX_API_BASE_URL: str = "http://localhost:8000"
    AUDIOFX_MODEL: str = "audiofx-default"
    PROMPT_COACH_ENABLED: bool = False
    PROMPT_COACH_MODEL: str = "gemini-2.5-flash"
    SCENE_DESCRIBER_ENABLED: bool = False
    SCENE_DESCRIBER_MODEL: str = "gemini-2.5-flash"
    SYNTHID_DASHBOARD_ENABLED: bool = False
    WORKSPACE_AUTOMATION_ENABLED: bool = False


settings = Settings()

# Create necessary directories
for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR, settings.TEMP_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True)
