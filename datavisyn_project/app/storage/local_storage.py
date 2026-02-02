import os
import uuid
from typing import BinaryIO
from pathlib import Path
from .base import StorageBackend
import logging
from fastapi import  HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalStorage(StorageBackend):
    def __init__(self):
        self.upload_dir = Path(os.getenv("UPLOAD_DIR"))
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save(self, file_id: uuid.UUID, file_content: BinaryIO, filename: str) -> str:
        """Save file to local filesystem"""
        try:
            stored_filename = f"{file_id}_{filename}"
            file_path = self.upload_dir/stored_filename
            logger.info(f"Start saving file to local path: {file_path}")
            # Write file content
            with open(file_path, "wb") as f:
                # Read in chunks for large files
                chunk_size = 8192
                while chunk := file_content.read(chunk_size):
                    f.write(chunk)
            logger.info(f"File saved successfully at: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving file {filename} to local storage: {str(e)}")
            raise
    
    
    async def read(self, file_name: str) -> bytes:
        """Read file from local filesystem"""
        try:
            # Find the file by UUID
            logger.info(f"Attempting to read file with ID: {file_name}")
            file_path = self.upload_dir / file_name
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_name}")
            with open(file_path, "rb") as f:
                content = f.read()
            logger.info(f"Read {len(content)} bytes from {file_name}")
            return content
        except FileNotFoundError:
            logger.error(f"File with ID {file_name} not found")     
            raise HTTPException(status_code=404, detail="File not found")
        
        except Exception as e:
            logger.error(f"Internal server error: Error reading file with ID {file_name}: {str(e)}")
            raise
    