import uuid
import io
import logging
import pandas as pd
from fastapi import HTTPException, status
from datavisyn_project.models.schema import file_schemas
from datavisyn_project.app.storage import get_storage_backend

logger = logging.getLogger(__name__)

DELIMITERS = [',', ';', '\t', '|']

async def read_file_info(file) -> file_schemas.FileMetadataCreate:
    """Extract metadata from uploaded CSV file and save to storage."""
    await _validate_csv_file(file)
    
    content = await file.read()
    file_id = uuid.uuid4()
    
    try:
        # Parse CSV metadata
        df, delimiter = await _parse_csv_metadata(content, file.filename)
        
        # Save to storage
        stored_filename = await _save_to_storage(file_id, content, file.filename)
        
        # Create metadata
        return file_schemas.FileMetadataCreate(
            id=file_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_size=len(content),
            row_count=len(df),
            column_count=len(df.columns),
            columns=df.columns.tolist(),
            delimiter=delimiter
        )
        
    finally:
        await file.close()


async def _validate_csv_file(file):
    """Validate file is CSV type."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only CSV files are allowed."
        )


async def _parse_csv_metadata(content: bytes, filename: str):
    """Parse CSV content and detect delimiter."""
    csv_data = io.StringIO(content.decode('utf-8'))
    
    # Detect delimiter
    delimiter = _detect_delimiter(csv_data, filename)
    
    # Parse full CSV
    csv_data.seek(0)
    try:
        df = pd.read_csv(csv_data, delimiter=delimiter)
    except Exception as e:
        raise HTTPException(400, f"Invalid CSV format: {str(e)}")
    
    logger.info(f"Parsed {filename}: {len(df)} rows, {len(df.columns)} columns")
    return df, delimiter


def _detect_delimiter(csv_data: io.StringIO, filename: str) -> str:
    """Detect CSV delimiter from sample."""
    for delimiter in DELIMITERS:
        try:
            csv_data.seek(0)
            df = pd.read_csv(csv_data, nrows=5, delimiter=delimiter)
            if len(df.columns) > 1:
                logger.info(f"Detected delimiter '{delimiter}' for {filename}")
                return delimiter
        except:
            continue
    
    logger.info(f"Using default delimiter ',' for {filename}")
    return ','  # Default


async def _save_to_storage(file_id: uuid.UUID, content: bytes, filename: str) -> str:
    """Save file to storage backend."""
    storage = get_storage_backend()
    file_stream = io.BytesIO(content)
    
    stored_filename = f"{file_id}_{filename}"
    await storage.save(file_id, file_stream, filename)
    
    logger.info(f"Saved {filename} to storage as {stored_filename}")
    return stored_filename