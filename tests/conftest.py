"""
Main conftest.py for the test suite.
Contains common fixtures, configurations, and utilities shared across all tests.
"""
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock

import pytest
from pydantic import UUID4


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_uuid():
    """Generate a mock UUID4 for testing."""
    return uuid.uuid4()


@pytest.fixture
def mock_uuid_str():
    """Generate a mock UUID4 string for testing."""
    return str(uuid.uuid4())


@pytest.fixture
def mock_datetime():
    """Generate a mock datetime for testing."""
    return datetime.now(timezone.utc)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id_": uuid.uuid4(),
        "username": "test_user",
        "metadata_": {"fullname": "Test User", "dob": "1990-01-01"},
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": None
    }


@pytest.fixture
def sample_post_data():
    """Sample post data for testing."""
    user_id = uuid.uuid4()
    return {
        "id_": uuid.uuid4(),
        "text_content": "This is a test post content",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "owner_id": user_id
    }


@pytest.fixture
def sample_comment_data():
    """Sample comment data for testing."""
    user_id = uuid.uuid4()
    post_id = uuid.uuid4()
    return {
        "id_": uuid.uuid4(),
        "text_content": "This is a test comment",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "post_id": post_id,
        "owner_id": user_id
    }


@pytest.fixture
def mock_container():
    """Mock dependency injection container."""
    container = Mock()
    container.config = Mock()
    container.wire = Mock()
    container.unwire = Mock()
    return container


@pytest.fixture
def mock_async_session():
    """Mock async database session."""
    session = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    return session


@pytest.fixture
def mock_repository():
    """Generic mock repository."""
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_multi = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_service():
    """Generic mock service."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_usecase():
    """Generic mock use case."""
    usecase = AsyncMock()
    return usecase


@pytest.fixture
def mock_unit_of_work():
    """Mock unit of work pattern."""
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    uow.posts = Mock()
    uow.comments = Mock()
    uow.users = Mock()
    return uow


class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, status_code: int = 200, json_data: Dict[str, Any] = None):
        self.status_code = status_code
        self._json_data = json_data or {}
    
    def json(self):
        return self._json_data
    
    async def aread(self):
        return str(self._json_data).encode()


@pytest.fixture
def mock_http_response():
    """Mock HTTP response."""
    return MockResponse()


# Test data generators
def generate_test_user_data(**overrides):
    """Generate test user data with optional overrides."""
    data = {
        "id_": uuid.uuid4(),
        "username": "test_user",
        "metadata_": {"fullname": "Test User"},
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": None
    }
    data.update(overrides)
    return data


def generate_test_post_data(**overrides):
    """Generate test post data with optional overrides."""
    data = {
        "id_": uuid.uuid4(),
        "text_content": "Test post content",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "owner_id": uuid.uuid4()
    }
    data.update(overrides)
    return data


def generate_test_comment_data(**overrides):
    """Generate test comment data with optional overrides."""
    data = {
        "id_": uuid.uuid4(),
        "text_content": "Test comment content",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
        "post_id": uuid.uuid4(),
        "owner_id": uuid.uuid4()
    }
    data.update(overrides)
    return data


# Utility functions for tests
def assert_entity_equality(entity1, entity2, exclude_fields=None):
    """Helper function to assert equality between entities."""
    exclude_fields = exclude_fields or []
    dict1 = entity1.to_dict() if hasattr(entity1, 'to_dict') else entity1.model_dump()
    dict2 = entity2.to_dict() if hasattr(entity2, 'to_dict') else entity2.model_dump()
    
    for field in exclude_fields:
        dict1.pop(field, None)
        dict2.pop(field, None)
    
    assert dict1 == dict2