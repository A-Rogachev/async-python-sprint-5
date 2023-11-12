
import redis
from fastapi import APIRouter, Depends

from db.redis_cache import get_redis_client
from db.storage_s3 import get_minio_client
from typing import Any
files_router: APIRouter = APIRouter()
from api.v1.authorization import oauth2_scheme, token_required
import minio
from db.db import get_session, async_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.users_service import users_crud
from models.user import User

# async def create_bucket_if_not_exists(minio_client):
#     try:
#         await minio_client.meta.client.head_bucket(Bucket='/test_bucket')
#     except ClientError:
#         await minio_client.create_bucket(
#             Bucket='test_bucket',
#             CreateBucketConfiguration={'LocationConstraint': 'your-region'})
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
from core.config import app_settings
import jwt
from fastapi import HTTPException

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
    user_id: int = user_model.id
    print(user_id)



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