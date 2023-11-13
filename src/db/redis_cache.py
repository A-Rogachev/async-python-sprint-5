import asyncio

import redis

from core.config import app_settings


async def get_redis_client() -> redis.Redis:
    """
    Возвращает клиента для работы с кешем.
    """
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    redis_client: redis.Redis = await loop.run_in_executor(
        None,
        lambda: redis.Redis(host=app_settings.REDIS_HOST, port=app_settings.REDIS_PORT),
    )
    return redis_client
