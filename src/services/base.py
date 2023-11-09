from datetime import datetime
from typing import Generic, Optional, Type, TypeVar
from abc import ABC, abstractmethod
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from passlib.hash import sha256_crypt
from pydantic import BaseModel
from sqlalchemy import select, update, exists, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
# DeleteSchemaType = TypeVar('DeleteSchemaType', bound=BaseModel)


class Repository(ABC):
    """
    Абстрактный класс репозитория для работы с БД.
    """

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError

    # @abstractmethod
    # def delete(self, *args, **kwargs):
    #     raise NotImplementedError


class UserRepositoryDB(
    Repository,
    Generic[ModelType, CreateSchemaType],
):
    """
    Репозиторий для работы с моделью ShortUrl.
    """
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def check_userdata_in_db(
        self,
        db: AsyncSession,
        user_data: dict[str, str],
    ) -> Optional[ModelType]:
        """
        Проверка на существование пользователя и электронной почты в БД.
        """
        statement = select(self._model).where(
            or_(
                self._model.username == user_data.get('username'),
                self._model.email == user_data.get('email')
            )
        )
        result = await db.execute(statement=statement)
        return result.scalar()


    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Создание нового пользователя.
        """
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        obj_in.password = pwd_context.hash(obj_in.password)
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    


    # async def delete(
    #     self,
    #     db: AsyncSession,
    #     obj_from_db: ModelType,
    #     obj_del_schema: DeleteSchemaType,
    # ) -> None:
    #     """
    #     Удаление записи.
    #     Для удаления записи требуется кодовое слово, записанное при создании.
    #     """
    #     if sha256_crypt.verify(
    #         obj_del_schema.password_for_deleting,
    #         obj_from_db.password_for_deleting,
    #     ):
    #         obj_from_db.deleted_at = datetime.now()
    #         await db.commit()
    #     else:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail='Wrong password for deleting',
    #         )

    # async def update_clicks_and_info(
    #     self,
    #     db: AsyncSession,
    #     obj_from_db: ModelType,
    #     client_ip: str,
    # ) -> None:
    #     """
    #     Обновление количества кликов и информации.
    #     """
    #     obj_from_db.total_clicks += 1
    #     if not obj_from_db.full_info:
    #         obj_from_db.full_info = {}
    #     full_info = obj_from_db.full_info
    #     full_info.update(
    #         {datetime.now().strftime("%Y-%m-%d %H:%M:%S"): client_ip}
    #     )
    #     statement = update(self._model).where(
    #         self._model.id == obj_from_db.id,
    #     ).values(full_info=full_info)
    #     await db.execute(statement=statement)
    #     await db.commit()