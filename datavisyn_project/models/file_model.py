from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid
from datavisyn_project.core.db_setup import Base

class CSVFiles(Base):
    __tablename__ = "csv_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_size = Column(BigInteger, nullable=False)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    row_count = Column(Integer)
    column_count = Column(Integer)
    columns = Column(JSON)  # Store column names
    delimiter = Column(String(10))


    
    