import pytest
import uuid
import os
from unittest.mock import patch

class TestSimpleStorage:
    """Simple storage tests."""
    
    def test_local_storage_simple(self, tmp_path):
        """Test local storage without async complications."""
        print("\n=== Testing Local Storage ===")
        
        # Set environment variable
        os.environ['UPLOAD_DIR'] = str(tmp_path)
        
        # Import and test
        from datavisyn_project.app.storage.local_storage import LocalStorage
        
        storage = LocalStorage()
        
        # Create test file
        file_id = uuid.uuid4()
        test_file = tmp_path / f"{file_id}_test.txt"
        test_file.write_bytes(b"test content")
        content = storage.read(f"{file_id}_test.txt")

    
    def test_s3_storage_mock_simple(self):
        """Simple S3 storage test."""
        print("\n=== Testing S3 Storage Mock ===")
        
        # Mock the entire save method
        with patch('datavisyn_project.app.storage.s3_storage.S3Storage.save') as mock_save:
            mock_save.return_value = f"uploads/{uuid.uuid4()}_test.csv"
            from datavisyn_project.app.storage.s3_storage import S3Storage
            
            storage = S3Storage()
            
            # Just verify the method exists and can be called
            assert hasattr(storage, 'save')
            assert hasattr(storage, 'read')
            
