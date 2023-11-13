from pydantic import BaseModel


class UploadFileRequest(BaseModel):
    """
    Схема, используемая при загрузке файла.
    """

    path: str


class UploadFileResponse(BaseModel):
    """
    Схема, используемая при успешной загрузке файла.
    """

    version_id: str
    name: str
    created_ad: str
    path: str
    size: int
