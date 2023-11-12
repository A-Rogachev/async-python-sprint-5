
from typing import Any, Optional

import jwt
import minio
import redis
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse

from api.v1.authorization import oauth2_scheme
from core.config import app_settings
from db.db import async_session, get_session
from db.redis_cache import get_redis_client
from db.storage_s3 import get_minio_client
from schemas.file_storage_schemas import UploadFileRequest, UploadFileResponse
from models.user import User
from services.users_service import users_crud
from api.v1.authorization import check_token
import os
files_router: APIRouter = APIRouter()
from starlette.responses import StreamingResponse
from minio.versioningconfig import VersioningConfig, ENABLED

async def create_bucket_if_not_exists(
    bucketname: str,
    minio_client: minio.Minio = Depends(get_minio_client),
):
    """
    Создает корзину для пользователя в хранилище, в случае если она не существует.
    """
    if not minio_client.bucket_exists(bucketname):
        minio_client.make_bucket(bucketname)
        minio_client.set_bucket_versioning(
            bucketname,
            VersioningConfig(ENABLED),
        )

async def get_path_name_for_file(path: str, filename: str):
    if not path:
        object_name = filename
    else:
        if path.endswith('/'):
            object_name = path + filename
        else:
            object_name = path
    return object_name


@files_router.post('/upload')
async def upload_file(
    file_to_upload: UploadFile = File(None),
    path: Optional[str] = Form(None) ,
    token: str = Depends(oauth2_scheme),
    redis_client: redis.Redis = Depends(get_redis_client),
    minio_client: minio.Minio = Depends(get_minio_client),
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Загрузка файла пользователем.
    """
    if not file_to_upload:
        raise HTTPException(status_code=400, detail='You must send a file')
    user_model: User = await users_crud.get_user_by_username(
        db=db,
        username=await check_token(token),
    )
    await create_bucket_if_not_exists(
        bucketname := f'storage-{user_model.id}',
        minio_client,
    )
    object_name: str = await get_path_name_for_file(path, file_to_upload.filename)
    # сделать проверку на совпадение имен.
    file_size: int = os.fstat(file_to_upload.file.fileno()).st_size
    response = minio_client.put_object(
        bucket_name=bucketname,
        object_name=object_name,
        data=file_to_upload.file,
        length=file_size,
        content_type=file_to_upload.content_type
    )
    print(response.version_id)
    

    # здесь записываем в базу postgres
    # ---------------------------------------------------------
    # to_postgres = {
    #     'id': 'some_id',
    #     'name': file_to_upload.filename,
    #     'created_ad': '2020-09-11T17:22:05Z',
    #     'size': file_size,
    #     'path': object_name,
    #     'is_downloadable': True
    # }
    # from pprint import pprint
    # pprint(to_postgres)
    # ---------------------------------------------------------

    return {"message": 'success'}


# {
#     "version_id": "a19ad56c-d8c6-4376-b9bb-ea82f7f5a853",
#     "name": "notes.txt",
#     "created_ad": "2020-09-11T17:22:05Z",
#     "path": "/homework/test-fodler/notes.txt",
#     "size": 8512,
#     "is_downloadable": true
# }




from pydantic import BaseModel

class DownloadFile(BaseModel):
    file_path: str
    file_id: Optional[str] = None

# TODO: здесь добавить возможность указать директорию для скачивания
@files_router.post('/download')
async def download_file(
    request_body: DownloadFile,
    token: str = Depends(oauth2_scheme),
    redis_client: redis.Redis = Depends(get_redis_client),
    minio_client: minio.Minio = Depends(get_minio_client),
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Скачивание файла из хранилища.
    """
    # TODO: если файл не найден, то is_downloadabale = False
    user_model: User = await users_crud.get_user_by_username(
        db=db,
        username=await check_token(token),
    )
    bucket_name: str = f'storage-{user_model.id}'
    response = minio_client.get_object(
        bucket_name=bucket_name,
        object_name=request_body.file_path,
    )
    file_content = response.read()
    return StreamingResponse(
        iter([file_content]),
        media_type='application/octet-stream',
        headers={'Content-Disposition': 'attachment; filename="file.txt"'},
    )
