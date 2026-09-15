from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "Recruitment AI"
    app_env: str = "development"
    debug: bool = True

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Groq
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"

    # Database
    database_url: str = "sqlite:///./data/recruitment.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()