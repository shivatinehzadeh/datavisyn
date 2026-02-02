import logging
from datavisyn_project.app.helper.enum import ServiceMethod
from datavisyn_project.app.decorators.error_handeling import handle_endpoint_errors
from datavisyn_project.models.schema import file_schemas
from .csv_factory.factory import CSVFileFactory
import uuid
from fastapi import APIRouter, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datavisyn_project.core.db_setup import get_async_session
from fastapi import Depends
from fastapi_cache.decorator import cache

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/upload_file/", response_model=file_schemas.UploadResponse, status_code=201)
@handle_endpoint_errors
async def upload_file(file: UploadFile = File(...), session: AsyncSession = Depends(get_async_session)):
    """Upload a CSV file to the system."""
    logger.info(f"Received upload request for file: {file.filename}")
    param = {"file": file, "db_session": session}
    uploading_file = await CSVFileFactory.get_service_method(ServiceMethod.SAVE_FILE, param).CSV_file()
    return file_schemas.UploadResponse.model_validate(uploading_file)

@router.get("/files", response_model=file_schemas.FileListResponse, status_code=200)
@handle_endpoint_errors
@cache(expire=60)
async def list_files(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_async_session)
):
    """List all uploaded files with pagination"""
    param = {"page": page, "page_size": page_size, "db_session": session}
    listed_files = await CSVFileFactory.get_service_method(ServiceMethod.GET_LISTED_FILES, param).CSV_file()
    return file_schemas.FileListResponse.model_validate(listed_files)

@router.get("/file/{file_id}/metadata", response_model=file_schemas.FileMetadataResponse, status_code=200)
@handle_endpoint_errors
async def file_metadata(file_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    """Get metadata for a specific file"""
    param = {"file_id": file_id, "db_session": session}
    file_metadata = await CSVFileFactory.get_service_method(
        ServiceMethod.GET_FILE_METADATA, param).CSV_file()
    return file_schemas.FileMetadataResponse.model_validate(file_metadata)
    
@router.get("/file/{file_id}/data", response_model=file_schemas.FileDataResponse, status_code=200)
@handle_endpoint_errors
@cache(expire=120)
async def get_file_data(
    file_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=100, description="Rows per page"),
    session: AsyncSession = Depends(get_async_session)
):
    logger.info(f"Retrieving data for file ID: {file_id}")
    """Get paginated data for a specific file"""
    param_db_file = {"file_id": file_id, "db_session": session}
    db_file = await CSVFileFactory.get_service_method(
                ServiceMethod.GET_FILE_METADATA,  param_db_file).CSV_file()
    param = {
        "file_id": file_id,
        "page": page,
        "page_size": page_size,
        "db_file": db_file
    }
    read_data =  await CSVFileFactory.get_service_method(ServiceMethod.READ_CSV_DATA, param).CSV_file()
    return file_schemas.FileDataResponse.model_validate(read_data)