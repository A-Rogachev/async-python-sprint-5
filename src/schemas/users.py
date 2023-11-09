from datetime import datetime

from pydantic import BaseModel


class AppUserBase(BaseModel):
    """
    Базовая модель для пользователя.
    """
    pass


class UserCreate(AppUserBase):
    """
    Схема, используемая при регистрации нового пользователя.
    """

    username: str
    password: str
    email: str


class UserToken(AppUserBase):
    """
    Схема, используемая для возврата токена при регистрации.
    """

class UserInDB(AppUserBase):
    """
    Схема, используемая для успешного ответа при регистрации пользователя.
    """

    id: int
    username: str
    email: str
    is_active: int
