from .base import AppBaseModel
from sqlalchemy import Column, Integer, String, DateTime


class User(AppBaseModel):
    """
    Модель пользователя.
    """

    __tablename__ = "users"

    id = Column(type_=Integer, primary_key=True)
    username = Column(type_=String(100), unique=True, nullable=False)
    password = Column(type_=String(100), nullable=False)
    email = Column(type_=String(100), unique=True, nullable=False)
    is_active = Column(type_=Integer, default=1)
