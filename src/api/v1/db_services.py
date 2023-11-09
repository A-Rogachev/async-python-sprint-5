from fastapi import APIRouter
import time
import psycopg2
import redis
from core.config import app_settings
from sqlalchemy import create_engine
from schemas.db_services import DbServicesPing

db_services_router: APIRouter = APIRouter()

@db_services_router.get('/ping', response_model=DbServicesPing)
async def ping() :
    """
    Получение информации о времени доступа ко всем связанным сервисам.
    """
    postgresql_response_time: str = await get_postgresql_ping_value()
    redis_response_time: str = await get_redis_ping_value()
    return DbServicesPing(
        postgresql_db=postgresql_response_time,
        redis_cache=f'{redis_response_time} seconds',
    )


async def get_redis_ping_value() -> str:
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


async def get_postgresql_ping_value() -> str:
    """
    Время доступа к базе данных postgresql.
    """
    postgresql_start_time = time.time()
    try:
        raise psycopg2.OperationalError
    except psycopg2.OperationalError:
        postgresql_response_time = 'not available'
    return postgresql_response_time
