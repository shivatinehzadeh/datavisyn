import os
from datavisyn_project.app.storage.local_storage import LocalStorage
from datavisyn_project.app.storage.s3_storage import S3Storage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_storage_backend():
    """Factory function to get the appropriate storage backend"""
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    logger.info(f"Initializing storage backend: {storage_type}")
    if storage_type == "s3":
        return S3Storage()
    else:
        return LocalStorage()