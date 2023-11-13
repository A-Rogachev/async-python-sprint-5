from models.user import User as UserModel
from schemas.user_schemas import UserCreate

from .base import UserRepositoryDB


class RepositoryUser(
    UserRepositoryDB[UserModel, UserCreate],
):
    """
    Бизнес логика для модели User.
    """
    pass


users_crud = RepositoryUser(UserModel)