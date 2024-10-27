from functools import lru_cache

from pydantic_settings import BaseSettings


class AppConfigs(BaseSettings):
    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str

    # API Settings
    API_TITLE: str = "Amazon Products Analytics API"
    API_VERSION: str = "0.0.1"
    API_DEBUG: bool = False

    # Security
    SECRET_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_config():
    return AppConfigs()
