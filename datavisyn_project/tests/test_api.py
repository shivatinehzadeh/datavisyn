from urllib import response
import pytest
import uuid
from unittest.mock import patch


test_uuid = uuid.uuid4()

class TestAPIEndpoints:
    """End-to-end API tests for CSV file upload flow."""
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self, test_client, mock_storage):
        """Test successful file upload."""
        with patch('datavisyn_project.app.storage.get_storage_backend', mock_storage):
            with patch('uuid.uuid4') as mock_uuid:
                
                mock_uuid.return_value = test_uuid
                
                csv_content = b"id,name,value\n1,Test,100\n2,Another,200"
                
                response = test_client.post(
                    "/api/upload_file/",
                    files={"file": ("data.csv", csv_content, "text/csv")}
                )
                
                assert response.status_code == 201
                data = response.json()
                assert data["file_id"] == str(test_uuid)
                assert data["filename"] == "data.csv"

                
                #get_file_details
                response = test_client.get(f"/api/file/{data["file_id"]}/data")

                assert response.status_code == 200
                data = response.json()
                assert len(data["data"]) > 1

    
    @pytest.mark.asyncio
    async def test_upload_file_invalid_type(self, test_client):
        """Test uploading non-CSV file."""
        response = test_client.post(
            "/api/upload_file/",
            files={"file": ("data.txt", b"plain text", "text/plain")}
        )
        
        assert response.status_code ==  400
    
    @pytest.mark.asyncio
    async def test_get_file_metadata(self, test_client, create_test_file_in_db):
        file_id = await create_test_file_in_db()   
        response = test_client.get(f"/api/file/{file_id}/metadata")
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_list_files(self, test_client, create_test_file_in_db):
        """Test listing files with pagination."""
        # Create multiple test files
        for i in range(5):
            await create_test_file_in_db(original_filename=f"file_{i}.csv")
        
        # Get first page with 2 files
        response = test_client.get("/api/files")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) == 5
        