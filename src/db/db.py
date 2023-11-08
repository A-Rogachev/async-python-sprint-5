from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import app_settings


load_dotenv()

engine: AsyncSession = create_async_engine(
    app_settings.database_dsn,
    echo=True if app_settings.is_debug else False,
    future=True
)
async_session: sessionmaker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
