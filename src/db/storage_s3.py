import asyncio
import os
from core.config import app_settings
from dotenv import load_dotenv
from minio import Minio

load_dotenv()


async def get_minio_client():
    """
    Возвращает клиента для работы с хранилищем.
    """
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    minio_client: Minio = await loop.run_in_executor(
        None,
        lambda: Minio(
            app_settings.MINIO_HOST,
            access_key=os.getenv('aws_access_key_id'),
            secret_key=os.getenv('aws_secret_access_key'),
            secure=False,
        )
    )
    return minio_client
