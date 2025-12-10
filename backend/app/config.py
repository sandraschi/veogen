from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings sourced from environment variables (.env by default).

    Gemini/GCP integration expects:
    - GEMINI_API_KEY for direct API fallback.
    - GOOGLE_API_KEY for MCP media server authentication.
    - GOOGLE_CLOUD_PROJECT naming the Vertex AI project.
    - GOOGLE_APPLICATION_CREDENTIALS pointing to a service account JSON when required.
    - GEMINI_CLI_PATH when the CLI binary is not discoverable on PATH.
    """
    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        case_sensitive=True,
    )

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "VeoGen - AI Video Generator"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered video generation using Google's Veo model via Gemini CLI.\n\nDefault admin user: admin / admin. Please change the password after first login."

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    WORKERS: int = 1

    # Google Cloud Configuration
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GOOGLE_API_KEY: Optional[str] = None

    # Gemini Configuration
    GEMINI_MODEL: str = "gemini-3.0-flash"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_CLI_PATH: Optional[str] = None

    # Veo Configuration
    VEO_MODEL: str = "veo-3.1"
    VEO_API_ENDPOINT: str = "https://aiplatform.googleapis.com"
    VEO_MAX_DURATION: int = 60
    VEO_DEFAULT_DURATION: int = 5

    # Flow / Flow Studio
    FLOW_ENABLED: bool = False
    FLOW_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/flow"
    FLOW_API_AUDIENCE: Optional[str] = None
    FLOW_WEBHOOK_SECRET: Optional[str] = None
    FLOW_DEFAULT_REGION: str = "us"

    # Scene Describer
    SCENE_DESCRIBER_MODEL: str = "gemini-3.0-pro-vision"
    SCENE_DESCRIBER_ENABLED: bool = False

    # Prompt Coach (Gemini Live)
    PROMPT_COACH_ENABLED: bool = False
    PROMPT_COACH_MODEL: str = "gemini-3.0-pro"

    # Imagen Configuration (Gemini 3 Pro Image - codename: Nano Banana Pro)
    IMAGEN_MODEL: str = "gemini-3.0-pro-image"

    # AudioFX / Sound Design
    AUDIOFX_ENABLED: bool = False
    AUDIOFX_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/audiofx"
    AUDIOFX_MODEL: str = "audiofx-1"

    # SynthID Compliance
    SYNTHID_DASHBOARD_ENABLED: bool = False
    SYNTHID_BIGQUERY_DATASET: Optional[str] = None

    # Workspace Automations
    WORKSPACE_AUTOMATION_ENABLED: bool = False
    WORKSPACE_AGENT_ID: Optional[str] = None

    # File Storage
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    TEMP_DIR: str = "temp"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_VIDEO_EXTENSIONS: set = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    # Video Generation Limits
    MAX_CONCURRENT_GENERATIONS: int = 3
    MAX_QUEUE_SIZE: int = 20
    GENERATION_TIMEOUT: int = 300  # 5 minutes

    # Database Configuration
    DATABASE_URL: Optional[str] = (
        "postgresql+asyncpg://veogen:veogen123@localhost:4715/veogen"
    )

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_ENABLED: bool = False

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:4710",  # Frontend port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:4710",  # Frontend port
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
        # Tailscale network access
        "http://goliath:4710",  # Tailscale hostname frontend
        "http://100.118.171.110:4710",  # Tailscale IP frontend
        "http://goliath:4700",  # Tailscale hostname backend API
        "http://100.118.171.110:4700",  # Tailscale IP backend API
        # Public IP access (for when port forwarding is enabled)
        "http://213.47.34.131:4710",  # Public IP frontend
        "http://213.47.34.131:4700",  # Public IP backend API
        "https://213.47.34.131:4710",  # Public IP frontend (HTTPS)
        "https://213.47.34.131:4700",  # Public IP backend API (HTTPS)
    ]

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "veogen.log"

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 8001

    # WebSocket
    WEBSOCKET_ENABLED: bool = True

    # Email Configuration
    EMAIL_FROM: str = "noreply@veogen.local"
    EMAIL_SMTP: str = "dev"  # 'dev' writes emails to file, otherwise SMTP host
    EMAIL_PORT: int = 25
    EMAIL_USER: str = ""
    EMAIL_PASS: str = ""
    EMAIL_DEV_OUTBOX: str = "dev_emails/"


settings = Settings()

# Create necessary directories
for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR, settings.TEMP_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True)
