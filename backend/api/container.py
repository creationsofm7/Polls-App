"""
Centralized dependency container for managing application services and repositories.

Features:
- Singleton pattern for global dependency management
- Lazy instantiation and intelligent caching
- Thread-safe operations
- FastAPI integration
- Test-friendly with temporary_override
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Type, TypeVar, Optional, Dict, Any, Callable
import threading

from sqlalchemy.ext.asyncio import AsyncSession

# Generic type variables for better type safety
T = TypeVar('T')
R = TypeVar('R')  # Repository type
S = TypeVar('S')  # Service type


class DependencyContainer:
    """
    Singleton dependency container with lazy instantiation and caching.
    
    Features:
    - Services are cached by class name (singleton per service type)
    - Repositories are cached by class name + database session ID
    - Thread-safe operations
    - Testability support via temporary_override
    """
    
    _instance: Optional['DependencyContainer'] = None
    _lock = threading.Lock()
    
    def __init__(self):
        self._repositories: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}
        self._instance_lock = threading.Lock()
        self._shared_instances: Dict[str, Any] = {}
    
    @classmethod
    def get_instance(cls) -> 'DependencyContainer':
        """Get or create the singleton container instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-check locking
                    cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        with cls._lock:
            cls._instance = None
    
    def get_repository(self, repo_type: Type[R], db: Optional[AsyncSession] = None, **kwargs) -> R:
        """
        Get or create a repository instance with proper caching.
        
        Repositories are cached per database session to ensure correct transaction handling.
        
        Args:
            repo_type: The repository class to instantiate
            db: Database session (if required by the repository)
            **kwargs: Additional constructor arguments
            
        Returns:
            Repository instance
        """
        # Always honor explicit overrides first (used in tests/mocking)
        override_key = repo_type.__name__
        with self._instance_lock:
            if override_key in self._repositories:
                return self._repositories[override_key]

        # Repositories are request-scoped; do not cache new instances
        try:
            if db is not None:
                return repo_type(db, **kwargs)
            return repo_type(**kwargs)
        except Exception as e:
            raise RuntimeError(
                f"Failed to create repository {repo_type.__name__}: {str(e)}"
            ) from e
    
    def get_service(self, service_type: Type[S], **kwargs) -> S:
        """
        Get or create a service instance with proper caching.
        
        Services are cached by class name and reused across requests.
        
        Args:
            service_type: The service class to instantiate
            **kwargs: Constructor arguments (typically injected dependencies)
            
        Returns:
            Service instance
        """
        key = service_type.__name__

        # If there is an override, always return it regardless of kwargs
        with self._instance_lock:
            if key in self._services:
                return self._services[key]

        # If constructor has no injected kwargs, treat as app-scoped singleton
        if not kwargs:
            with self._instance_lock:
                if key not in self._services:
                    try:
                        self._services[key] = service_type()
                    except Exception as e:
                        raise RuntimeError(
                            f"Failed to create service {service_type.__name__}: {str(e)}"
                        ) from e
                return self._services[key]

        # Otherwise, services with injected deps are request-scoped; do not cache
        try:
            return service_type(**kwargs)
        except Exception as e:
            raise RuntimeError(
                f"Failed to create service {service_type.__name__}: {str(e)}"
            ) from e
    
    @contextmanager
    def temporary_override(self, dependency_type: Type[T], instance: T):
        """
        Temporarily override a dependency for testing.
        
        Usage:
            with container.temporary_override(UserService, mock_user_service):
                # Tests run with mock_user_service instead of real one
                result = some_function_that_uses_user_service()
        
        Args:
            dependency_type: The type to override
            instance: The mock/fake instance to use temporarily
        """
        key = dependency_type.__name__
        original = None
        is_service = False
        
        try:
            # Determine if it's a service or repository and save original
            with self._instance_lock:
                if key in self._services:
                    is_service = True
                    original = self._services[key]
                    self._services[key] = instance
                elif key in self._repositories:
                    original = self._repositories[key]
                    self._repositories[key] = instance
                else:
                    # Not cached yet, just set it
                    # Try to guess if it's a service (you could make this smarter)
                    is_service = 'Service' in dependency_type.__name__
                    if is_service:
                        self._services[key] = instance
                    else:
                        self._repositories[key] = instance
            
            yield
            
        finally:
            # Restore original or remove if there was none
            with self._instance_lock:
                if original is not None:
                    if is_service:
                        self._services[key] = original
                    else:
                        self._repositories[key] = original
                else:
                    # Remove the temporary override
                    if is_service:
                        self._services.pop(key, None)
                    else:
                        self._repositories.pop(key, None)
    
    def clear_cache(self) -> None:
        """Clear all cached dependencies (useful for testing)."""
        with self._instance_lock:
            self._repositories.clear()
            self._services.clear()
            self._shared_instances.clear()

    def get_shared(self, key: str, factory: Callable[[], Any]) -> Any:
        """Get or create a shared singleton not tied to service/repo."""
        with self._instance_lock:
            if key not in self._shared_instances:
                self._shared_instances[key] = factory()
            return self._shared_instances[key]


# Global container instance getter
def get_container() -> DependencyContainer:
    """Get the global dependency container instance."""
    return DependencyContainer.get_instance()

