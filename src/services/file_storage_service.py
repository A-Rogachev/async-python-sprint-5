from typing import Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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

    async def get_all_user_records(
        self,
        user_id: int,
        db: AsyncSession
    ) -> list[ModelType]:
        """
        Возвращает все записи в БД о загруженных файлах.
        """
        statement = select(self._model).filter_by(user_id=user_id)
        result = await db.execute(statement=statement)
        return result.scalars().all()
    

uploaded_files_crud = FileStorageRepositoryDB(UploadedFile)
