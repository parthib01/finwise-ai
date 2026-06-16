# src/app/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FinWise AI"

    DATABASE_URL: str

    REDIS_HOST: str
    REDIS_PORT: int

    class Config:
        env_file = ".env"


settings = Settings()