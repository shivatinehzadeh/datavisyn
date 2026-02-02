from ..helper.enum import ServiceMethod
from .save_file import SaveFileService
from .get_file_list import GetListedFilesService
from .get_metadata import GetFileMetadata
from .get_file_detail import GetFileDetail
from .base import CSVFileService

class CSVFileFactory:
    @staticmethod
    def get_service_method(method: ServiceMethod,input=None) -> CSVFileService:
        """Available service methods for CSV file operations."""
        
        if method == ServiceMethod.SAVE_FILE:
            """save and upload csv file to storage and save metadata to database"""
            return SaveFileService(input)
        
        elif method == ServiceMethod.GET_LISTED_FILES:
            """Retrieve a paginated list of uploaded files."""
            return GetListedFilesService(input)
        
        elif method == ServiceMethod.GET_FILE_METADATA:
            """Get metadata for a specific file."""
            return GetFileMetadata(input)
        
        elif method == ServiceMethod.READ_CSV_DATA:
            """Read and paginate CSV file content."""
            return GetFileDetail(input)
        
        else:
            raise ValueError("Invalid Factory method")