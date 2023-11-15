import os

from dotenv import load_dotenv
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

load_dotenv()


class AppSettings(BaseSettings):
    """
    Настройки приложения.
    """

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    APP_TITLE: str
    DATABASE_DSN: PostgresDsn
    IS_DEBUG: bool
    MAX_FILE_SIZE: int
    MAX_FILE_SIZE_IN_MB: int
    MINIO_HOST: str
    REDIS_DB: int
    REDIS_HOST: str
    REDIS_PORT: int
    SECRET_KEY: str

    class Config:
        """
        Настройки конфигурации.
        """

        env_file = '.env'


app_settings: AppSettings = AppSettings()
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
