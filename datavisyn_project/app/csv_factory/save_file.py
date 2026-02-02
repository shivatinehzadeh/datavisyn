from datavisyn_project.app.helper.enum import StorageRepositoryType
from datavisyn_project.app.helper.file_processor import read_file_info
from datavisyn_project.app.repository_dp.factory import RepositoryFactory
import logging
import logging
from .base import CSVFileService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


        
        
class SaveFileService(CSVFileService):
    def __init__(self, input):
        self.file = input["file"]
        self.db_session = input["db_session"]
        
    async def _run(self):
        try:   
            
            logger.info(f"Starting upload for file: {self.file.filename}")
            file_info = await read_file_info(self.file)
            logger.info(f"File info extracted: {file_info}")
            
            #save file metadata to database
            get_repository = RepositoryFactory.get_repository(StorageRepositoryType.FILE_METADATA,
                                                              self.db_session)
            print(f"Repository obtained: {get_repository}, file_info: {file_info}   ")
            save_file = await get_repository.create_file_metadata(file_info)
            logger.info(f"File {self.file.filename} uploaded successfully with ID {str(save_file.id)}")
            
            return {
                    "message": "File uploaded successfully",
                    "file_id": save_file.id,
                    "filename": save_file.original_filename,
                    "file_size": save_file.file_size,
                    "row_count": save_file.row_count,
                    "column_count": save_file.column_count
                    }
        except KeyError:
                self.log_error("Missing 'file' in input")
                raise ValueError("Missing 'file' in input")
        except AttributeError as e:
            self.log_error(f"Invalid file object: {e}")
            raise ValueError(f"Invalid file object: {e}")