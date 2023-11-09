from pydantic import BaseModel, EmailStr


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
    email: EmailStr


class UserAuth(BaseModel):
    """
    Схема, используемая для авторизации пользователя (получения токена).
    """

    username: str
    password: str


class UserToken(AppUserBase):
    """
    Схема, используемая для возврата токена при регистрации.
    """
    access_token: str
    token_type: str


class UserInDB(AppUserBase):
    """
    Схема, используемая для успешного ответа при регистрации пользователя.
    """

    id: int
    username: str
    email: EmailStr
    is_active: int
