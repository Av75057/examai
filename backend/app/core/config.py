from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "ExamAI"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://examai:examai_secret@localhost:5432/examai"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    openai_api_key: str = ""
    openai_model: str = "deepseek-v4-flash"
    openai_base_url: str = "https://api.deepseek.com"

    free_tasks_per_day: int = 5
    premium_monthly_price: int = 990


@lru_cache()
def get_settings() -> Settings:
    return Settings()
