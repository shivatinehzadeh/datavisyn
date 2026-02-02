

from fastapi import HTTPException
from .base import CSVFileService
from datavisyn_project.app.helper.enum import StorageRepositoryType
from datavisyn_project.app.repository_dp.factory import RepositoryFactory


class GetFileMetadata(CSVFileService):
    def __init__(self, input):
        self.file_id = input["file_id"]
        self.db_session = input["db_session"]
        
    async def _run(self):
        """Retrieve and return the file metadata from the database"""
        self.log_info(f"Fetching metadata for file ID: {self.file_id}")
        
        get_repository = RepositoryFactory.get_repository(StorageRepositoryType.FILE_METADATA, self.db_session)
        db_file = await get_repository.get_file(self.file_id)
        if not db_file:
            self.log_error("File not found in database")
            raise HTTPException(status_code=404, detail="File not found")
        return {
            "id": str(db_file.id),
            "original_filename": db_file.original_filename,
            "stored_filename": db_file.stored_filename,
            "upload_timestamp": str(db_file.upload_timestamp.isoformat())if db_file.upload_timestamp else None,
            "file_size": db_file.file_size,
            "row_count": db_file.row_count,
            "column_count": db_file.column_count,
            "delimiter": db_file.delimiter
        }
