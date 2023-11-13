import time

import psycopg2
import redis
from fastapi import APIRouter, Depends

from api.v1.authorization import check_token, oauth2_scheme
from core.config import app_settings
from db.redis_cache import get_redis_client
from schemas.db_services import DbServicesPing

db_services_router: APIRouter = APIRouter()


@db_services_router.get('/ping', response_model=DbServicesPing)
async def ping(
    token: str = Depends(oauth2_scheme),
    redis_client: redis.Redis = Depends(get_redis_client),
) -> DbServicesPing:
    """
    Получение информации о времени доступа ко всем связанным сервисам.
    """
    check_token(token)
    postgresql_response_time: str = await get_postgresql_ping_value()
    redis_response_time: str = await get_redis_ping_value()
    return DbServicesPing(
        postgresql_db=f'{postgresql_response_time:.5f} seconds',
        redis_cache=f'{redis_response_time:.5f} seconds',
    )


async def get_redis_ping_value() -> str | float:
    """
    Время доступа к базе данных для кеширования токенов пользователей.
    """
    redis_start_time = time.time()
    try:
        with redis.Redis(host='localhost', port=6379, db=0) as redis_client:
            redis_client.ping()
            redis_response_time = round(time.time() - redis_start_time, 5)
    except redis.ConnectionError:
        redis_response_time = 'not available'
    return redis_response_time


async def get_postgresql_ping_value() -> str | float:
    """
    Время доступа к базе данных postgresql.
    """
    postgresql_start_time = time.time()
    try:
        dsn = str(app_settings.DATABASE_DSN).replace('+asyncpg', '')
        connection = psycopg2.connect(dsn=dsn)
        postgresql_response_time = round(time.time() - postgresql_start_time, 5)
        connection.close()
    except psycopg2.OperationalError:
        postgresql_response_time = 'not available'
    return postgresql_response_time
