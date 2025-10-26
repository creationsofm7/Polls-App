from typing import List, Optional
from ..repos.interfaces.poll_repository import IPollRepository
from ..schemas.poll import PollCreate, Poll
from ..exceptions import NotFoundException
from ..utils.decorators import service_error_logger
from ..events import PollEventBus
from ..events.bus import build_poll_event


class PollService:
    def __init__(self, poll_repository: IPollRepository, event_bus: Optional[PollEventBus] = None):
        self.poll_repository = poll_repository
        self.event_bus = event_bus

    @service_error_logger("create_poll")
    async def create_poll(self, user_id: int, payload: PollCreate) -> Poll:
        poll = await self.poll_repository.create_poll(user_id=user_id, payload=payload)
        if self.event_bus:
            event = build_poll_event("poll_created", poll)
            await self.event_bus.publish(event)
        return poll

    @service_error_logger("get_poll")
    async def get_poll(self, poll_id: int) -> Poll:
        poll = await self.poll_repository.get_poll(poll_id)
        if not poll:
            raise NotFoundException("Poll not found")
        return poll

    @service_error_logger("list_polls")
    async def list_polls(self, *, limit: int = 50, offset: int = 0) -> List[Poll]:
        return await self.poll_repository.list_polls_detailed(limit=limit, offset=offset)

    @service_error_logger("like_poll")
    async def like_poll(self, poll_id: int, user_id: int) -> Poll:
        poll = await self.poll_repository.like_poll(poll_id=poll_id, user_id=user_id)
        if self.event_bus:
            event = build_poll_event("poll_updated", poll)
            await self.event_bus.publish(event)
        return poll

    @service_error_logger("dislike_poll")
    async def dislike_poll(self, poll_id: int, user_id: int) -> Poll:
        poll = await self.poll_repository.dislike_poll(poll_id=poll_id, user_id=user_id)
        if self.event_bus:
            event = build_poll_event("poll_updated", poll)
            await self.event_bus.publish(event)
        return poll

    @service_error_logger("list_polls_ranked")
    async def list_polls_ranked(self, by: str = "created_at", *, limit: int = 50, offset: int = 0) -> List[Poll]:
        return await self.poll_repository.list_polls_detailed(sort_by=by, limit=limit, offset=offset)

    @service_error_logger("list_polls_by_user")
    async def list_polls_by_user(self, user_id: int, by: str = "created_at", *, limit: int = 50, offset: int = 0) -> List[Poll]:
        return await self.poll_repository.list_polls_by_user_detailed(user_id=user_id, sort_by=by, limit=limit, offset=offset)

    @service_error_logger("delete_poll")
    async def delete_poll(self, poll_id: int) -> None:
        await self.poll_repository.delete_poll(poll_id=poll_id)
        if self.event_bus:
            # For delete, we only send poll_id since poll is gone
            from ..events import PollEvent
            event = PollEvent(event_type="poll_deleted", payload={"poll_id": poll_id})
            await self.event_bus.publish(event)

