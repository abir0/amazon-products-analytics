from functools import lru_cache

from pydantic_settings import BaseSettings


class AppConfigs(BaseSettings):
    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str

    # Amazon Scraper
    SCRAPER_INTERVAL_MINUTES: int = 60
    SCRAPER_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_RETRY_DELAY: int = 5

    # API Settings
    API_TITLE: str = "Amazon Products Analytics API"
    API_VERSION: str = "0.0.1"
    API_DEBUG: bool = False

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_config():
    return AppConfigs()
