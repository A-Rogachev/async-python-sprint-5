from typing import Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from models.uploaded_file import UploadedFile
from schemas.file_storage_schemas import UploadFileResponse

ModelType = TypeVar('ModelType', bound=UploadedFile)
CreateSchemaType = TypeVar('CreateSchemaType', bound=UploadFileResponse)


class FileStorageRepositoryDB:
    """
    Репозиторий для работы с моделью UploadedFile (файл хранилища).
    """
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def create_record(
        self,
        db: AsyncSession,
        uploaded_file_data
    ) -> ModelType:
        """
        Создание нового записи в БД о загруженном файле.
        """
        file_obj = self._model(**uploaded_file_data)
        db.add(file_obj)
        await db.commit()
        await db.refresh(file_obj)
        return file_obj

    # async def get_user_by_username(
    #     self,
    #     db: AsyncSession,
    #     username: str,
    # ) -> Optional[ModelType]:
    #     """
    #     Поиск пользователя по имени.
    #     """
    #     statement = select(self._model).where(
    #         self._model.username == username
    #     )
    #     result = await db.execute(statement=statement)
    #     return result.scalar_one_or_none()

uploaded_files_crud = FileStorageRepositoryDB(UploadedFile)
