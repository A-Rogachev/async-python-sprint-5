import datetime

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

    id: str
    name: str
    created_ad: str
    path: str
    size: int
    is_downloadable: bool
# {
#     "id": "a19ad56c-d8c6-4376-b9bb-ea82f7f5a853",
#     "name": "notes.txt",
#     "created_ad": "2020-09-11T17:22:05Z",
#     "path": "/homework/test-fodler/notes.txt",
#     "size": 8512,
#     "is_downloadable": true
# }
