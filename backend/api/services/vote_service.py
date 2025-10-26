from typing import Optional, List, Dict
from ..repos.interfaces.vote_repository import IVoteRepository
from ..repos.interfaces.poll_repository import IPollRepository
from ..schemas.vote import VoteCreate, Vote
from ..utils.decorators import service_error_logger
from ..events import PollEventBus
from ..events.bus import build_poll_event


class VoteService:
    def __init__(
        self, 
        vote_repository: IVoteRepository,
        poll_repository: Optional[IPollRepository] = None,
        event_bus: Optional[PollEventBus] = None
    ):
        self.vote_repository = vote_repository
        self.poll_repository = poll_repository
        self.event_bus = event_bus

    @service_error_logger("cast_vote")
    async def cast_vote(self, user_id: int, payload: VoteCreate) -> Vote:
        vote = await self.vote_repository.cast_vote(user_id=user_id, payload=payload)
        
        # Emit poll update event if we have both event_bus and poll_repository
        if self.event_bus and self.poll_repository:
            poll = await self.poll_repository.get_poll_with_users(payload.poll_id)
            if poll:
                event = build_poll_event("poll_updated", poll)
                await self.event_bus.publish(event)
        
        return vote

    @service_error_logger("get_user_vote_for_poll")
    async def get_user_vote_for_poll(self, user_id: int, poll_id: int) -> Optional[Vote]:
        return await self.vote_repository.get_user_vote_for_poll(user_id=user_id, poll_id=poll_id)

    @service_error_logger("list_user_votes_for_polls")
    async def list_user_votes_for_polls(self, user_id: int, poll_ids: List[int]) -> Dict[int, int]:
        return await self.vote_repository.list_user_votes_for_polls(user_id=user_id, poll_ids=poll_ids)

