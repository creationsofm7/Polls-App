from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from ...schemas.vote import VoteCreate
from ...models.votes import Vote


class IVoteRepository(ABC):
    @abstractmethod
    async def cast_vote(self, user_id: int, payload: VoteCreate) -> Vote:
        pass

    @abstractmethod
    async def get_user_vote_for_poll(self, user_id: int, poll_id: int) -> Optional[Vote]:
        pass

    @abstractmethod
    async def list_user_votes_for_polls(self, user_id: int, poll_ids: List[int]) -> Dict[int, int]:
        """Return mapping of poll_id -> option_id for the given user."""
        pass

