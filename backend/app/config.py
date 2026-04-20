from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


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
        env_file=".env",
        case_sensitive=True,
    )

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "VeoGen Industrial"
    VERSION: str = "3.1.0"
    DESCRIPTION: str = "SOTA 2026 AI Video & Media Generation Platform.\n\nFeaturing Gemini 3.1, Veo 3.1, Lyria 3, and Nano Banana 2."

    # Server Configuration (Fleet Standard)
    HOST: str = "0.0.0.0"
    PORT: int = 10730
    FRONTEND_PORT: int = 10731
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

    # Database Configuration
    DATABASE_URL: Optional[str] = (
        "postgresql+asyncpg://veogen:veogen123@localhost:4715/veogen"
    )

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_ENABLED: bool = False

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # CORS (Standardized for Fleet)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:10731",
        "http://127.0.0.1:10731",
        "http://localhost:10730",
        "http://127.0.0.1:10730",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "veogen.log"

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 10732

    # Email Configuration (Legacy support)
    EMAIL_FROM: str = "noreply@veogen.local"
    EMAIL_SMTP: str = "dev"
    EMAIL_DEV_OUTBOX: str = "dev_emails/"


settings = Settings()

# Create necessary directories
for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR, settings.TEMP_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True)
