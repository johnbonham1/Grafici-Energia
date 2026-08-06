from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Dashboard AEIF API"
    environment: str = "local"
    database_url: str = "sqlite:///./dashboard_aeif.db"
    cors_origins: str = Field(
        default="http://localhost:8000,http://localhost:5173,https://dashboard-aeif.onrender.com,https://johnbonham1.github.io,https://dashboard-aeif-preprod.onrender.com,https://dashboard-aeif-preproduzione.onrender.com"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
