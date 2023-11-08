from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

Base = declarative_base()

class AppBaseModel(Base):
    """
    Базовый класс моделей приложения.
    """
    __abstract__ = True
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    updated_at = Column(DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, index=True)
