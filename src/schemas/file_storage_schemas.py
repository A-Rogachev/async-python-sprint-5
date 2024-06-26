from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DownloadFile(BaseModel):
    """
    Схема, используемая при скачивании файла.
    """
    file_path: str
    version_id: Optional[str] = None


class UploadFileResponse(BaseModel):
    """
    Схема, используемая при успешной загрузке файла.
    """

    version_id: str
    name: str
    created_at: datetime
    path: str
    size: int


class UserFilesResponse(BaseModel):
    """
    Схема, используемая для получения информации о загруженных файлах.
    """

    user_id: int
    user_name: str
    files_count: int
    files: list[UploadFileResponse]
