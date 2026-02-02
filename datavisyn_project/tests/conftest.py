import pytest
import asyncio
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datavisyn_project.core.db_setup import Base, get_async_session
from datavisyn_project.core.base import app

os.environ["STORAGE_TYPE"] = "local"
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db_session():
    """Create test database session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncTestingSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncTestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
def test_client(test_db_session):
    """FastAPI test client with database dependency override."""
    
    async def override_get_async_session():
        yield test_db_session
    
    # Store original overrides
    original_overrides = app.dependency_overrides.copy()
    
    # Apply test overrides
    app.dependency_overrides[get_async_session] = override_get_async_session
    
    with TestClient(app) as client:
        yield client
    
    # Restore original overrides
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)

@pytest.fixture
def mock_storage():
    """Mock storage backend."""
    storage = AsyncMock()
    storage.save = AsyncMock(return_value="test_stored_filename.csv")
    storage.read = AsyncMock(return_value=b"id,name,age\n1,John,25\n2,Jane,30\n3,Bob,35")
    storage.get_file_path = AsyncMock(return_value="/mock/path/test.csv")
    storage.exists = AsyncMock(return_value=True)
    storage.save.return_value = "mocked/path/test.csv"
    return storage


@pytest.fixture
def create_test_file_in_db(test_db_session):
    """Helper to create a test file in database."""
    async def _create_test_file(file_id=None, original_filename="test.csv"):
        from datavisyn_project.models.file_model import CSVFiles
        import datetime
        
        if file_id is None:
            file_id = uuid.uuid4()
        
        test_file = CSVFiles(
            id=file_id,
            original_filename=original_filename,
            stored_filename=f"{file_id}_{original_filename}",
            file_size=1024,
            upload_timestamp=datetime.datetime.utcnow(),
            row_count=3,
            column_count=3,
            columns=json.dumps(["id", "name", "age"]),
            delimiter=","
        )
        
        test_db_session.add(test_file)
        await test_db_session.commit()
        return file_id
    
    return _create_test_file