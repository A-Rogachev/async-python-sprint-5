from fastapi import FastAPI
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import os

load_dotenv()

# async def get_minio_client():
#     # credentials = Credentials(
#     #     access_key='YOUR_ACCESS_KEY',
#     #     secret_key='YOUR_SECRET_KEY'
#     # )
#     minio_client = Minio(
#         'localhost:9000',
#         access_key=os.getenv('aws_access_key_id'),
#         secret_key=os.getenv('aws_secret_access_key'),
#         secure=False,
#     )
#     yield minio_client

import asyncio

async def get_minio_client():
    """
    Возвращает клиента для работы с хранилищем.
    """
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    minio_client: Minio = await loop.run_in_executor(
        None,
        lambda: Minio(
            'localhost:9000',
            access_key=os.getenv('aws_access_key_id'),
            secret_key=os.getenv('aws_secret_access_key'),
            secure=False,
        )
    )
    return minio_client