from sqlalchemy import Column,String,DateTime,Integer,JSON,Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from database.db import Base

class Document(Base):
    __tablename__="documents"

    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    file_name=Column(String,nullable=False)
    storage_path=Column(String,nullable=False)
    status=Column(String,default="uploaded")
    text_content = Column(String, nullable=True)
    created_at=Column(DateTime, default=datetime.utcnow)

class DocumentChunk(Base):

    __tablename__ = "document_chunks"

    id= Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id = Column(UUID(as_uuid=True), nullable=False)

    chunk_text = Column(Text, nullable=False)

    chunk_index = Column(Integer)

    embedding = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
