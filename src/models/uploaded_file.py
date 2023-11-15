from .base import AppBaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class UploadedFile(AppBaseModel):
    """
    Запись с информацией о загруженном файле.
    """

    __tablename__ = "uploaded_files"

    id = Column(type_=Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    version_id = Column(type_=String(100), nullable=False, index=True)
    name = Column(type_=String(100), nullable=False)
    size = Column(type_=Integer, nullable=False)
    path = Column(type_=String(100), nullable=False)

    user = relationship('User', back_populates='uploaded_files')
    # NOTE: в случае совпадения пути, в хранилище записывается новая версия файла,
    # старая доступна по version_id
