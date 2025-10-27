from typing import Optional, List, Dict
from ..repos.interfaces.vote_repository import IVoteRepository
from ..repos.interfaces.poll_repository import IPollRepository
from ..schemas.vote import VoteCreate, Vote
from ..schemas.poll import Poll
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
    async def cast_vote(self, user_id: int, payload: VoteCreate) -> Poll:
        vote = await self.vote_repository.cast_vote(user_id=user_id, payload=payload)
        
        # Get the updated poll with user's vote information
        if self.poll_repository:
            poll = await self.poll_repository.get_poll_with_users(payload.poll_id)
            if poll:
                # Convert to Poll schema and add my_vote_option_id
                poll_response = Poll.from_orm(poll)
                poll_response.my_vote_option_id = vote.option_id
                
                # Emit poll update event if we have event_bus
                if self.event_bus:
                    event = build_poll_event("poll_updated", poll)
                    await self.event_bus.publish(event)
                
                return poll_response
        
        # Fallback: if poll_repository is not available, return a minimal response
        # This shouldn't happen in normal operation but provides safety
        raise RuntimeError("Poll repository not available for vote casting")

    @service_error_logger("get_user_vote_for_poll")
    async def get_user_vote_for_poll(self, user_id: int, poll_id: int) -> Optional[Vote]:
        return await self.vote_repository.get_user_vote_for_poll(user_id=user_id, poll_id=poll_id)

    @service_error_logger("list_user_votes_for_polls")
    async def list_user_votes_for_polls(self, user_id: int, poll_ids: List[int]) -> Dict[int, int]:
        return await self.vote_repository.list_user_votes_for_polls(user_id=user_id, poll_ids=poll_ids)

