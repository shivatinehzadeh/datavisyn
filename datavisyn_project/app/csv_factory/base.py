from fastapi import  HTTPException
import logging
from abc import ABC, abstractmethod


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVFileService(ABC):
    def __init__(self, input):
        self.input = input
        
    def log_info(self, message: str):
        logger.info(f"{self.__class__.__name__}:{message}")
    
    def log_warning(self, message: str):
        logger.warning(f"{self.__class__.__name__}:{message}")
    
    def log_error(self, message: str):
        logger.error(f"{self.__class__.__name__}:{message}")
            
    async def CSV_file(self):
        try:
            return await self._run()   

        except ConnectionError:
            self.log_error("Cannot connect to storage service")
            raise HTTPException(503, "Cannot connect to storage service")
        
        except TimeoutError:
            raise HTTPException(504, "Storage service timeout")
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise  # Re-raise existing HTTP exceptions
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            raise HTTPException(
                status_code=500,
                detail={"error": "Internal server error", "request_id": "..."}
            )
    
    @abstractmethod
    async def _run(self):
        pass
    
