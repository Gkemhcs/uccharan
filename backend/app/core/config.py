from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    google_api_key: str
    gemini_model: str = "gemini-3.6-flash"
    cors_origins: str = "*"
    # Not a secret — it's the same project id already baked into the seed
    # scripts and the Android app's google-services.json. Auth verification
    # only needs it to check a token's audience/issuer, never to sign anything.
    firebase_project_id: str = "uccharan-87bcf"

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — env is read once per process."""
    return Settings()
