import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):

    # App
    # APP_NAME:  str = os.environ.get("APP_NAME", "FastAPI")
    # DEBUG: bool = bool(os.environ.get("DEBUG", False))
    
    # FrontEnd Application
    FRONTEND_HOST: str = os.environ.get("FRONTEND_HOST", "http://localhost:3000")

    # POSTGRESQL Database Config
    POSTGRESQL_HOST: str = os.environ.get("POSTGRESQL_HOST", 'localhost')
    POSTGRESQL_USER: str = os.environ.get("POSTGRESQL_USER", 'postgres')
    POSTGRESQL_PASS: str = os.environ.get("POSTGRESQL_PASSWORD", 'password')
    POSTGRESQL_PORT: int = int(os.environ.get("POSTGRESQL_PORT", 5432))
    POSTGRESQL_DB: str = os.environ.get("POSTGRESQL_DB", 'authen')
    # DB URI
    SQLALCHEMY_DATABASE_URL : str = f"postgresql+asyncpg://{POSTGRESQL_USER}:%s@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}" % quote_plus(POSTGRESQL_PASS)

    # EMAIL config
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    MAIL_PORT : int = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER : str = os.getenv("MAIL_SERVER","smtp.gmail.com")

    # REDIS
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_URL: str = os.getenv(f"REDIS_URL", f"redis://localhost:6379/0")

    # JWT Secret Key
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "649fb93ef34e4fdf4187709c84d643dd61ce730d91856418fdcf563f895ea40f")
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 3))
    # REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES", 1440))

    # Azure Blob Storage Config
    AZURE_CONNECTION_STRING: str = os.environ.get("AZURE_CONNECTION_STRING", "")
    AZURE_ACCOUNT_NAME: str = os.environ.get("AZURE_ACCOUNT_NAME", "mercuonestorage")
    AZURE_CONTAINER_NAME: str = os.environ.get("AZURE_CONTAINER_NAME", "vehicle-imageclassify")

    # App Secret Key
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "8deadce9449770680910741063cd0a3fe0acb62a8978661f421bbcbb66dc41f1")


@lru_cache()
def get_settings() -> Settings:
    return Settings()