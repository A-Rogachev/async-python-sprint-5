
from typing import Any
from aiohttp import ClientError

import jwt
import minio
import redis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.authorization import oauth2_scheme, token_required
from core.config import app_settings
from db.db import async_session, get_session
from db.redis_cache import get_redis_client
from db.storage_s3 import get_minio_client
from models.user import User
from services.users_service import users_crud

files_router: APIRouter = APIRouter()


async def get_user_id_from_token(
    token: str,
) -> str:
    """
    Возвращает имя пользователя.
    """
    return jwt.decode(
        token,
        app_settings.SECRET_KEY,
        algorithms=[app_settings.ALGORITHM]
    ).get('sub')


async def create_bucket_if_not_exists(
    bucketname: str,
    minio_client: minio.Minio = Depends(get_minio_client),
):
    """
    Создает корзину для пользователя в хранилище, в случае если она не существует.
    """
    if not minio_client.bucket_exists(bucketname):
        minio_client.make_bucket(bucketname)

@files_router.post('/upload')
@token_required
async def upload_file(
    token: str = Depends(oauth2_scheme),
    redis_client: redis.Redis = Depends(get_redis_client),
    minio_client: minio.Minio = Depends(get_minio_client),
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Загрузка файла пользователем.
    """
    user_name: str = await get_user_id_from_token(token)
    user_model: User = await users_crud.get_user_by_username(
        db=db,
        username=user_name,
    )
    await create_bucket_if_not_exists(
        bucketname := f'storage-{user_model.id}',
        minio_client,
    )


    # print(minio_client.list_buckets())
    # import os
    # await minio_client.meta.client.upload_file(
    #     '../example.txt',
    #     '/test_bucket',
    #     'file.txt',
    # )
    return {"message": 'success'}


# {
#     "path": <full-path-to-file>||<path-to-folder>,
# }

# Response

# {
#     "id": "a19ad56c-d8c6-4376-b9bb-ea82f7f5a853",
#     "name": "notes.txt",
#     "created_ad": "2020-09-11T17:22:05Z",
#     "path": "/homework/test-fodler/notes.txt",
#     "size": 8512,
#     "is_downloadable": true
# }