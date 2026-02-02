from abc import ABC, abstractmethod
from typing import BinaryIO
import uuid
from typing import Optional

class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def save(self, file_id: uuid.UUID, file_content: BinaryIO, filename: str) -> str:
        pass
    
    @abstractmethod
    async def read(self, file_name:str) -> bytes:
        pass

