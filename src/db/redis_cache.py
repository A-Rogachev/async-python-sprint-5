import asyncio

import redis
from dotenv import load_dotenv

load_dotenv()

async def get_redis_client() -> redis.Redis:
    """
    Возвращает клиента для работы с кешем.
    """
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    redis_client: redis.Redis = await loop.run_in_executor(
        None,
        lambda: redis.Redis(host='localhost', port=6379)
    )
    return redis_client
