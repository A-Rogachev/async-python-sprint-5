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
    try:
        raise psycopg2.OperationalError
    except psycopg2.OperationalError:
        postgresql_response_time = 'not available'

    redis_start_time = time.time()
    try:
        with redis.Redis(host='localhost', port=6379, db=0) as redis_client:
            redis_client.ping()
            redis_response_time = round(time.time() - redis_start_time, 5)
    except redis.ConnectionError:
        redis_response_time = 'not available'

    return DbServicesPing(
        postgresql_db=postgresql_response_time,
        redis_cache=f'{redis_response_time} seconds',
    )
