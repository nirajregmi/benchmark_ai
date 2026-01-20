from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, Field

class Settings(BaseSettings):
    """
    Application core settings using Pydantic.
    Reads from .env file or environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Observability Platform"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    CORS_ORIGINS: List[str] = [
        "http://localhost:5174",  # Vite default
        "http://localhost:3000",
    ]

    # Prometheus Settings
    PROMETHEUS_URL: AnyHttpUrl = Field(
        default="http://localhost:9090",
        description="URL of the Prometheus instance"
    )
    PROMETHEUS_TOKEN: Optional[str] = Field(
        default=None,
        description="Bearer token for Prometheus authentication"
    )

    # LLM Settings (LLaMA-3.3-70B via generic OpenAI-compatible API usually)
    LLM_API_URL: AnyHttpUrl = Field(
        ...,
        description="Endpoint for the LLM provider"
    )
    LLM_API_KEY: str = Field(
        ...,
        description="API Key for the LLM provider"
    )
    LLM_MODEL: str = "llama-3.3-70b"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 1024

    # Intelligence Pipeline
    MAX_METRIC_POINTS: int = 100  # Downsample large datasets for LLM context

settings = Settings()
