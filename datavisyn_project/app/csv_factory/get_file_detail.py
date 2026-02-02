
import io
import json
from fastapi import HTTPException
import pandas as pd
from .base import CSVFileService
from datavisyn_project.app.helper.enum import ServiceMethod
from datavisyn_project.app.storage import get_storage_backend
from pandas.errors import ParserError

class GetFileDetail(CSVFileService):
    def __init__(self, input):
        self.file_id = input["file_id"]
        self.page = input["page"]
        self.page_size = input["page_size"]
        self.db_file = input["db_file"]

    async def _run(self):
        """Retrieve and return the CSV data"""
        try:
            self.log_info(f"Fetching data for file ID: {self.file_id} with page: {self.page}, page_size: {self.page_size}")
            
            
            # Read file from storage
            
            storage = get_storage_backend()
            file_content = await storage.read(self.db_file.get("stored_filename"))
            self.log_info(f"File content of size {len(file_content)} bytes read from storage")
            # Parse CSV
            csv_data = io.StringIO(file_content.decode('utf-8'))
            df = pd.read_csv(csv_data, delimiter=self.db_file.get("delimiter"))
            
            # Apply pagination
            total_rows = len(df)
            total_pages = (total_rows + self.page_size - 1) // self.page_size
            
            if self.page > total_pages and total_rows > 0:
                raise HTTPException(400, "Page out of range")
            
            start_idx = (self.page - 1) * self.page_size
            end_idx = start_idx + self.page_size
            
            paginated_df = df.iloc[start_idx:end_idx]
            paginated_data = json.loads(
                paginated_df.to_json(orient="records", date_format="iso")
            )
            self.log_info(f"Returning {len(paginated_data)} rows for page {self.page} of {total_pages}")
            return {
                "id": self.file_id,
                "filename": self.db_file.get("original_filename"),
                "data": paginated_data,
                "total_rows": total_rows,
                "page": self.page,
                "page_size": self.page_size,
                "total_pages": total_pages
            }

        except ParserError as e:  
            self.log_warning(f"CSV parsing failed: {e}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error_type": "invalid_csv",
                    "message": f"CSV file format is invalid: {str(e)}",
                    "suggestion": "Please check your CSV file for formatting issues"
                }
            )    

            