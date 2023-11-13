import os

from dotenv import load_dotenv
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

load_dotenv()


class AppSettings(BaseSettings):
    """
    Настройки приложения.

    :param is_debug: Режим отладки.
    :param app_title: Название приложения.
    :param database_dsn: Строка подключения к базе данных.
    """
    is_debug: bool
    app_title: str
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_DSN: PostgresDsn


    class Config:
        """
        Настройки конфигурации.

        :param env_file: Файл с настройками.
        """
        env_file = '.env'


app_settings: AppSettings = AppSettings()
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
