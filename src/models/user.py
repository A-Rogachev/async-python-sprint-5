from .base import AppBaseModel
from sqlalchemy import Column, Integer, String, DateTime


class User(AppBaseModel):
    """
    Модель пользователя.
    """

    __tablename__ = "users"

    id = Column(type_=Integer, name='id', primary_key=True)
    username = Column(type_=String(100), name='Имя', unique=True, nullable=False)
    password = Column(type_=String(100), name='Пароль', nullable=False)
    email = Column(type_=String(100), name='Электронная почта', unique=True, nullable=False)
    is_active = Column(type_=Integer, name='Активен', default=1)
