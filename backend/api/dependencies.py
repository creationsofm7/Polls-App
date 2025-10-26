"""
FastAPI dependency injection providers.

This module provides FastAPI-compatible dependency functions that use the
centralized DependencyContainer for instance management.
"""

from fastapi import Depends
from typing import TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

from .container import get_container
from .database import get_db
from .repos.interfaces.user_repository import IUserRepository
from .repos.postgres.users import PostgresUserRepository
from .repos.interfaces.poll_repository import IPollRepository
from .repos.postgres.polls import PostgresPollRepository
from .repos.interfaces.vote_repository import IVoteRepository
from .repos.postgres.votes import PostgresVoteRepository
from .services.user_service import UserService
from .services.poll_service import PollService
from .services.vote_service import VoteService
from .events import PollEventBus

if TYPE_CHECKING:
    from .auth import AuthService


# Repository providers
def get_user_repository(db: AsyncSession = Depends(get_db)) -> IUserRepository:
    """Get user repository instance from the container."""
    container = get_container()
    return container.get_repository(PostgresUserRepository, db=db)

def get_poll_repository(db: AsyncSession = Depends(get_db)) -> IPollRepository:
    """Get poll repository instance from the container."""
    container = get_container()
    return container.get_repository(PostgresPollRepository, db=db)

def get_vote_repository(db: AsyncSession = Depends(get_db)) -> IVoteRepository:
    """Get vote repository instance from the container."""
    container = get_container()
    return container.get_repository(PostgresVoteRepository, db=db)


# Shared instances
def get_poll_event_bus() -> PollEventBus:
    """Get the singleton PollEventBus instance."""
    container = get_container()
    return container.get_shared("poll_event_bus", PollEventBus)


# Service providers
def get_user_service(
    user_repo: IUserRepository = Depends(get_user_repository)
) -> UserService:
    """Get user service instance from the container."""
    container = get_container()
    return container.get_service(UserService, user_repository=user_repo)


def get_auth_service(
    user_repo: IUserRepository = Depends(get_user_repository)
) -> "AuthService":
    """Get auth service instance from the container."""
    from .auth import AuthService
    container = get_container()
    return container.get_service(AuthService, user_repository=user_repo)


def get_poll_service(
    poll_repo: IPollRepository = Depends(get_poll_repository),
    event_bus: PollEventBus = Depends(get_poll_event_bus),
) -> PollService:
    container = get_container()
    return container.get_service(PollService, poll_repository=poll_repo, event_bus=event_bus)


def get_vote_service(
    vote_repo: IVoteRepository = Depends(get_vote_repository),
    poll_repo: IPollRepository = Depends(get_poll_repository),
    event_bus: PollEventBus = Depends(get_poll_event_bus),
) -> VoteService:
    container = get_container()
    return container.get_service(
        VoteService, 
        vote_repository=vote_repo,
        poll_repository=poll_repo,
        event_bus=event_bus
    )
