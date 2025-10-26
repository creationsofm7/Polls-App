from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ...schemas.poll import PollCreate
from ...models.polls import Poll, PollOption


class IPollRepository(ABC):
    @abstractmethod
    async def create_poll(self, user_id: int, payload: PollCreate) -> Poll:
        pass

    @abstractmethod
    async def get_poll(self, poll_id: int) -> Optional[Poll]:
        pass

    @abstractmethod
    async def list_polls(self, *, limit: int = 50, offset: int = 0) -> List[Poll]:
        pass

    @abstractmethod
    async def list_polls_detailed(self, *, sort_by: str = "created_at", limit: int = 50, offset: int = 0) -> List[Poll]:
        """Return polls with creator, options, liked_by, disliked_by eagerly loaded."""
        pass

    @abstractmethod
    async def list_polls_by_user_detailed(self, user_id: int, *, sort_by: str = "created_at", limit: int = 50, offset: int = 0) -> List[Poll]:
        pass

    @abstractmethod
    async def get_poll_with_users(self, poll_id: int) -> Optional[Poll]:
        """Return a single poll with liked_by/disliked_by users eagerly loaded."""
        pass

    @abstractmethod
    async def like_poll(self, poll_id: int, user_id: int) -> Poll:
        pass

    @abstractmethod
    async def dislike_poll(self, poll_id: int, user_id: int) -> Poll:
        pass

    @abstractmethod
    async def delete_poll(self, poll_id: int) -> None:
        pass

