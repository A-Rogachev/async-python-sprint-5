from datetime import timedelta
from functools import wraps
import inspect
import jwt
import redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as fs_status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import app_settings
from db.db import get_session
from db.redis_cache import get_redis_client
from models.user import User
from schemas.users import UserAuth, UserCreate, UserInDB, UserToken
from services.users_service import users_crud
from typing import Optional
from minio import Minio
from db.storage_s3 import get_minio_client

users_router: APIRouter = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def token_required(function):
    @wraps(function)
    async def wrapper(
        token: str = Depends(oauth2_scheme),
        redis_client: redis.Redis = Depends(get_redis_client),
        minio_client: Optional[Minio] = Depends(get_minio_client),
        db: Optional[AsyncSession] = Depends(get_session),
    ):
        try:
            username = jwt.decode(
                token,
                app_settings.SECRET_KEY,
                algorithms=[app_settings.ALGORITHM])['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired.')
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail='Missing or invalid token.')
        if not redis_client.get(username):
            raise HTTPException(status_code=401, detail='Missing or invalid token.')
        need_args = {}
        if 'db' in inspect.signature(function).parameters:
            need_args['db'] = db
        if 'minio_client' in inspect.signature(function).parameters:
            need_args['minio_client'] = minio_client
        if 'redis_client' in inspect.signature(function).parameters:
            need_args['redis_client'] = redis_client
        return await function(token, **need_args)
    return wrapper


@users_router.post('/register', response_model=UserInDB, status_code=fs_status.HTTP_201_CREATED)
async def register_user(
    *,
    db: AsyncSession = Depends(get_session),
    user_creating: UserCreate,
) -> UserInDB:
    """
    Регистрация нового пользователя.
    """
    user_with_this_data_exists = await users_crud.check_userdata_in_db(
        db,
        user_data={'username': user_creating.username, 'email': user_creating.email},
    )
    if bool(user_with_this_data_exists):
        raise HTTPException(
            status_code=fs_status.HTTP_400_BAD_REQUEST,
            detail='Record with the same username or email already exists'
        )
    new_record: User = await users_crud.create(db=db, obj_in=user_creating)
    return new_record


@users_router.post("/auth")
async def authenticate_user(
    *,
    db: AsyncSession = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis_client),
    user_authentication: UserAuth,
) -> UserToken:
    user: User | None = await users_crud.get_user_by_username(
        db=db,
        username=user_authentication.username,
    )
    if not user or not users_crud.verify_password(user_authentication.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = users_crud.create_access_token(
        {"sub": user.username},
        timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    redis_client.set(user.username, access_token)
    return UserToken(
        access_token=access_token,
        token_type="bearer"
    )
