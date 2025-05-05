from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True  # ¡Importante! Esto evita que se cree una tabla para esta clase.

    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)# para que el id sea un uuid
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
