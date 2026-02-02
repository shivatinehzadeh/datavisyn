
from .base import CSVFileService
from datavisyn_project.app.helper.enum import StorageRepositoryType
from datavisyn_project.app.repository_dp.factory import RepositoryFactory
from fastapi import HTTPException


class GetListedFilesService(CSVFileService):
    def __init__(self, input):
        self.page = input["page"]
        self.page_size = input["page_size"]
        self.db_session = input["db_session"]
        
    async def _run(self): 
        """Retrieve and return a paginated list of file metadata from the database"""
        # Calculate skip
        skip = (self.page - 1) * self.page_size
        get_repository = RepositoryFactory.get_repository(StorageRepositoryType.FILE_METADATA, self.db_session)

        # Count total
        total_files = await get_repository.count_files()
        
        if skip >= total_files and total_files > 0:
            self.log_error("Page out of range")
            raise HTTPException(400, "Page out of range")
        
        # Get files
        get_listed_files = await get_repository.get_file_list(skip=skip, limit=self.page_size)
        
        files_list = [
            {
                "id": file.id,
                "original_filename": file.original_filename,
                "stored_filename": file.stored_filename,
                "upload_timestamp": file.upload_timestamp.isoformat() if file.upload_timestamp else None,
                "file_size": file.file_size,
                "row_count": file.row_count,
                "column_count": file.column_count,
                "delimiter": file.delimiter

            }
            for file in get_listed_files
            ]
        
        return {
            "files": files_list,
            "total": total_files,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": (total_files + self.page_size - 1) // self.page_size
        }
        
