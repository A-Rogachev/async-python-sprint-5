
import os
from typing import Any, Optional

import jwt
import minio
import redis
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.authorization import check_token, oauth2_scheme
from core.config import app_settings
from db.db import async_session, get_session
from db.redis_cache import get_redis_client
from db.storage_s3 import get_minio_client
from models.user import User
from schemas.file_storage_schemas import UploadFileResponse, DownloadFile, UserFilesResponse
from services.file_storage_service import uploaded_files_crud
from services.users_service import users_crud
from minio.error import S3Error

from minio.versioningconfig import ENABLED, VersioningConfig
from starlette.responses import StreamingResponse

files_router: APIRouter = APIRouter()

async def create_bucket_if_not_exists(
    bucketname: str,
    minio_client: minio.Minio = Depends(get_minio_client),
):
    """
    Создает корзину для пользователя в хранилище, в случае если она не существует.
    Включает версионирование для корзины для возможности загружать различные
    версии одинакового файла.
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

    file_size: int = os.fstat(file_to_upload.file.fileno()).st_size

    try:
        response = minio_client.put_object(
            bucket_name=bucketname,
            object_name=object_name,
            data=file_to_upload.file,
            length=file_size,
            content_type=file_to_upload.content_type
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    else:
        try:
            new_uploaded_file_record = await uploaded_files_crud.create_record(
                db,
                uploaded_file_data = dict(
                    version_id=response.version_id,
                    user_id=user_model.id,
                    name=file_to_upload.filename,
                    size=file_size,
                    path=object_name,
                )
            )
        except Exception as create_record_error:
            raise HTTPException(status_code=400, detail=str(create_record_error))
        else:
            return UploadFileResponse(
                **new_uploaded_file_record.__dict__
            ).model_dump()


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
    user_model: User = await users_crud.get_user_by_username(
        db=db,
        username=await check_token(token),
    )
    bucket_name: str = f'storage-{user_model.id}'
    try:
        if request_body.file_path is None:
            response = minio_client.get_object(
                bucket_name=bucket_name,
                object_name=request_body.file_path,
            )
        else:
            response = minio_client.get_object(
                bucket_name=bucket_name,
                object_name=request_body.file_path,
                version_id=request_body.version_id
            )
    except S3Error:
        raise HTTPException(status_code=404, detail='Ошибка при загрузке файла')
    file_content = response.read()
    return StreamingResponse(
        iter([file_content]),
        media_type='application/octet-stream',
        headers={'Content-Disposition': 'attachment; filename="file.txt"'},
    )


@files_router.get('/')
async def get_all_user_files(
    token: str = Depends(oauth2_scheme),
    redis_client: redis.Redis = Depends(get_redis_client),
    minio_client: minio.Minio = Depends(get_minio_client),
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Возвращает информацию о всех загруженных пользователем файлах.
    """
    user_model: User = await users_crud.get_user_by_username(
        db=db,
        username=await check_token(token),
    )
    all_records = await uploaded_files_crud.get_all_user_records(
        user_model.id,
        db,
    )
    return UserFilesResponse(
        user_id=user_model.id,
        user_name=user_model.username,
        files_count=len(all_records),
        files=[
            UploadFileResponse(**record.__dict__).model_dump()
            for record
            in all_records
        ],
    )
