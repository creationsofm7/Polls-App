"""
Example tests demonstrating the DependencyContainer's temporary_override feature.

This shows how to mock dependencies for isolated unit testing.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from api.container import get_container
from api.services.user_service import UserService
from api.repos.postgres.users import PostgresUserRepository
from api.schemas.user import User


@pytest.mark.asyncio
async def test_with_mocked_user_service():
    """
    Example: Override UserService with a mock for testing.
    
    This allows you to test routes/logic that depend on UserService
    without needing a real database or authentication.
    """
    container = get_container()
    
    # Create a mock service
    mock_user_service = Mock(spec=UserService)
    mock_user_service.authenticate_user = AsyncMock(return_value=Mock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        is_admin=False
    ))
    
    # Use temporary_override to replace the real service with the mock
    with container.temporary_override(UserService, mock_user_service):
        # Inside this context, any code that requests UserService
        # from the container will get the mock instead
        
        # Example: Your route handler would call container.get_service(UserService)
        service = container.get_service(UserService)
        
        # Verify it's the mock
        assert service is mock_user_service
        
        # Test with the mock
        user = await service.authenticate_user("test@example.com", "password")
        assert user.email == "test@example.com"
    
    # After the context, the original service is restored
    # (or removed if it wasn't cached before)


@pytest.mark.asyncio
async def test_with_mocked_repository():
    """
    Example: Override a repository with a mock.
    
    Useful for testing services without database access.
    """
    container = get_container()
    
    # Create a mock repository
    mock_repo = Mock(spec=PostgresUserRepository)
    mock_repo.get_user_by_email = AsyncMock(return_value=Mock(
        id=1,
        email="test@example.com",
        hashed_password="hashed_pw",
        full_name="Test User",
        is_admin=False
    ))
    
    with container.temporary_override(PostgresUserRepository, mock_repo):
        repo = container.get_repository(PostgresUserRepository, db=None)
        
        assert repo is mock_repo
        
        user = await repo.get_user_by_email("test@example.com")
        assert user.email == "test@example.com"


def test_container_clear_cache():
    """
    Example: Clear container cache between tests.
    
    Useful in test setup/teardown to ensure clean state.
    """
    container = get_container()
    
    # Cache some items
    mock_service = Mock(spec=UserService)
    with container.temporary_override(UserService, mock_service):
        pass
    
    # Clear all cached dependencies
    container.clear_cache()
    
    # Container is now empty and ready for fresh instances


def test_container_reset_instance():
    """
    Example: Reset the entire container singleton.
    
    Use this in test fixtures for complete isolation.
    """
    from api.container import DependencyContainer
    
    # Get current instance
    container1 = DependencyContainer.get_instance()
    
    # Reset the singleton
    DependencyContainer.reset_instance()
    
    # Get a new instance
    container2 = DependencyContainer.get_instance()
    
    # They're different objects
    assert container1 is not container2

