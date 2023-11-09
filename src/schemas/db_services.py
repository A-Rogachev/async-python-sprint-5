from pydantic import BaseModel


class DbServicesPing(BaseModel):
    """
    Схема, используемая при ответе о доступности сервисов БД.
    """

    postgresql_db: str
    redis_cache: str
