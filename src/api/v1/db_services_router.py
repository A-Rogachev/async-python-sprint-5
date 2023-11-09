from fastapi import FastAPI
import time
import psycopg2
import redis

app = FastAPI()

@app.get("/ping")
async def ping():
    # Проверка доступности PostgreSQL
    db_start_time = time.time()
    try:
        conn = psycopg2.connect(
            host="filestorage_db",
            port=5432,
            user="your_username",
            password="your_password",
            database="your_database",
        )
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        db_end_time = time.time()
        db_response_time = db_end_time - db_start_time
    except psycopg2.Error:
        db_response_time = None

    # Проверка доступности Redis
    cache_start_time = time.time()
    try:
        r = redis.Redis(host="filestorage_redis", port=6379)
        r.ping()
        cache_end_time = time.time()
        cache_response_time = cache_end_time - cache_start_time
    except redis.ConnectionError:
        cache_response_time = None

    # Возвращаем время доступа к PostgreSQL и Redis в виде JSON-ответа
    return {
        "db": db_response_time,
        "cache": cache_response_time,
    }