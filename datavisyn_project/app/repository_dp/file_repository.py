import uuid
from datavisyn_project.models.schema import file_schemas 
from datavisyn_project.models.file_model import CSVFiles
from sqlalchemy import desc
from typing import Optional, List
from sqlalchemy import select


class FileMetadataRepository:
    
    def __init__(self, db_session):
        self.db = db_session
        
    async def create_file_metadata(self, file_metadata: file_schemas.FileMetadataCreate) -> CSVFiles:
        db_file = CSVFiles(**file_metadata.dict())
        self.db.add(db_file)
        await self.db.commit()
        await self.db.refresh(db_file)
        return db_file
    
    async def get_file_list(self, skip: int = 0, limit: int = 100) -> List[CSVFiles]:
        selecting_data = select(CSVFiles).order_by(desc(CSVFiles.upload_timestamp)).offset(skip).limit(limit)
        result = await self.db.execute(selecting_data)
        return result.scalars().all()
    
    async def get_file(self, file_id: uuid.UUID) -> Optional[CSVFiles]:
        selecting_data = select(CSVFiles).where(CSVFiles.id == file_id)
        result = await self.db.execute(selecting_data)
        return result.scalar_one_or_none()
    
    async def count_files(self) -> int:
        from sqlalchemy import func, select
        selecting_data = select(func.count()).select_from(CSVFiles)
        result = await self.db.execute(selecting_data)
        return result.scalar()