import time

import psycopg2
import redis
from fastapi import APIRouter, Depends
import aioboto3
from api.v1.authorization import oauth2_scheme, token_required
from core.config import app_settings
from db.redis_cache import get_redis_client
from db.storage_s3 import get_minio_client
from schemas.db_services import DbServicesPing
from typing import Any
files_router: APIRouter = APIRouter()
from botocore.exceptions import ClientError
import minio

# async def create_bucket_if_not_exists(minio_client):
#     try:
#         await minio_client.meta.client.head_bucket(Bucket='/test_bucket')
#     except ClientError:
#         await minio_client.create_bucket(
#             Bucket='test_bucket',
#             CreateBucketConfiguration={'LocationConstraint': 'your-region'})
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")

@files_router.post('/upload')
async def upload_file(
    minio_client: minio.Minio = Depends(get_minio_client),
) -> Any:
    """
    Загрузка файла пользователем.
    """
    # minio_client.make_bucket('testbucket')
    print(minio_client.list_buckets())
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