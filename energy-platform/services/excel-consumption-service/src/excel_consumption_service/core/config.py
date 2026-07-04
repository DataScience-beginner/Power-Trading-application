from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service settings loaded from environment variables."""

    service_name: str = "excel-consumption-service"
    environment: str = "development"
    database_url: str = "sqlite:///./data/excel_consumption.db"
    upload_dir: str = "./data/uploads"
    default_tenant: str = "demo-tenant"
    jwt_secret: str = "change-this-before-production-with-at-least-32-characters"
    access_token_expire_minutes: int = 480
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:4173"])

    model_config = SettingsConfigDict(
        env_prefix="EXCEL_CONSUMPTION_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
