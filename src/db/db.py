from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import app_settings


load_dotenv()

engine: AsyncSession = create_async_engine(
    str(app_settings.DATABASE_DSN),
    echo=True if app_settings.is_debug else False,
    future=True
)
async_session: sessionmaker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
