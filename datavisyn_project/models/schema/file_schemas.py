from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class FileMetadataBase(BaseModel):
    original_filename: str
    file_size: int


class FileMetadataCreate(FileMetadataBase):
    id: uuid.UUID
    stored_filename: str
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    columns: Optional[List[str]] = None
    delimiter: Optional[str] = None
    original_filename: str
    file_size: int
    
    
class FileMetadataResponse(FileMetadataBase):
    id: uuid.UUID
    stored_filename: str
    upload_timestamp: str
    row_count: Optional[int]
    column_count: Optional[int]
    delimiter: Optional[str]
    class Config:
        from_attributes = True

class FileListResponse(BaseModel):
    files: List[FileMetadataResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class FileDataResponse(BaseModel):
    id: uuid.UUID
    filename: str
    data: List[Dict[str, Any]]
    total_rows: int
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None

class UploadResponse(BaseModel):
    message: str
    file_id: uuid.UUID
    filename: str
    file_size: int
    row_count: int
    column_count: int
