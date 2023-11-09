from datetime import timedelta

import redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as fs_status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import app_settings
from db.db import get_session
from models.user import User
from schemas.users import UserAuth, UserCreate, UserInDB, UserToken
from services.users_service import users_crud


users_router: APIRouter = APIRouter()


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
    with redis.Redis(host='localhost', port=6379, db=0) as redis_client:
        redis_client.set(user.username, access_token)
    return UserToken(
        access_token=access_token,
        token_type="bearer"
    )



from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
import jwt

@users_router.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    # Verify the access token from Redis
    username = jwt.decode(
        token,
        app_settings.SECRET_KEY,
        algorithms=[app_settings.ALGORITHM])["sub"]
    if not redis_client.get(username) == token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "Protected resource"}
