from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UploadFileRequest(BaseModel):
    """
    Схема, используемая при загрузке файла.
    """

    path: str


class DownloadFile(BaseModel):
    """
    Схема, используемая при скачивании файла.
    """
    file_path: str
    file_id: Optional[str] = None


class UploadFileResponse(BaseModel):
    """
    Схема, используемая при успешной загрузке файла.
    """

    version_id: str
    name: str
    created_at: datetime
    path: str
    size: int
