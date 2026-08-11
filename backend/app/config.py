from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Dashboard AEIF API"
    environment: str = "local"
    database_url: str = "sqlite:///./dashboard_aeif.db"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-nano"
    cors_origins: str = Field(
        default="http://localhost:8000,http://localhost:5173,https://dashboard-aeif-preprod.onrender.com"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
