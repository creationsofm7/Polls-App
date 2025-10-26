from fastapi import APIRouter, Depends, status, HTTPException
from typing import Literal, List
from sse_starlette.sse import EventSourceResponse
from ..dependencies import get_poll_service, get_vote_service, get_poll_event_bus
from ..services.poll_service import PollService
from ..services.vote_service import VoteService
from ..auth import get_current_user_simple, get_optional_user_simple
from ..schemas.poll import PollCreate, Poll
from ..schemas.user import User
from ..events import PollEventBus
from pydantic import BaseModel
import json


router = APIRouter(prefix="/polls", tags=["Polls"])


class PollListRequest(BaseModel):
    sort_by: Literal["created_at", "likes"] = "created_at"
    limit: int = 50
    offset: int = 0


@router.post("/", response_model=Poll, status_code=status.HTTP_201_CREATED)
async def create_poll(
    payload: PollCreate,
    current_user: User = Depends(get_current_user_simple),
    poll_service: PollService = Depends(get_poll_service),
):
    return await poll_service.create_poll(user_id=current_user.id, payload=payload)


@router.delete("/{poll_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_poll(
    poll_id: int,
    current_user: User = Depends(get_current_user_simple),
    poll_service: PollService = Depends(get_poll_service),
):
    poll = await poll_service.get_poll(poll_id)
    if (poll.created_by != current_user.id) and (not current_user.is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete this poll")
    await poll_service.delete_poll(poll_id=poll_id)
    return None


@router.post("/list", response_model=List[Poll])
async def list_polls(
    body: PollListRequest,
    poll_service: PollService = Depends(get_poll_service),
    vote_service: VoteService = Depends(get_vote_service),
    maybe_user: User | None = Depends(get_optional_user_simple),
):
    polls = await poll_service.list_polls_ranked(by=body.sort_by, limit=body.limit, offset=body.offset)
    if not maybe_user:
        return polls
    poll_ids = [p.id for p in polls]
    mapping = await vote_service.list_user_votes_for_polls(user_id=maybe_user.id, poll_ids=poll_ids)
    # Ensure my_vote_option_id is included in response
    enriched: List[Poll] = []
    for p in polls:
        enriched.append(Poll.from_orm(p).copy(update={"my_vote_option_id": mapping.get(p.id)}))
    return enriched


@router.post("/mine", response_model=List[Poll])
async def list_my_polls(
    body: PollListRequest,
    current_user: User = Depends(get_current_user_simple),
    poll_service: PollService = Depends(get_poll_service),
    vote_service: VoteService = Depends(get_vote_service),
):
    polls = await poll_service.list_polls_by_user(user_id=current_user.id, by=body.sort_by, limit=body.limit, offset=body.offset)
    poll_ids = [p.id for p in polls]
    mapping = await vote_service.list_user_votes_for_polls(user_id=current_user.id, poll_ids=poll_ids)
    enriched: List[Poll] = []
    for p in polls:
        enriched.append(Poll.from_orm(p).copy(update={"my_vote_option_id": mapping.get(p.id)}))
    return enriched


@router.post("/{poll_id}/like", response_model=Poll)
async def like_poll(
    poll_id: int,
    current_user: User = Depends(get_current_user_simple),
    poll_service: PollService = Depends(get_poll_service),
):
    return await poll_service.like_poll(poll_id=poll_id, user_id=current_user.id)


@router.post("/{poll_id}/dislike", response_model=Poll)
async def dislike_poll(
    poll_id: int,
    current_user: User = Depends(get_current_user_simple),
    poll_service: PollService = Depends(get_poll_service),
):
    return await poll_service.dislike_poll(poll_id=poll_id, user_id=current_user.id)


@router.get("/stream")
async def stream_poll_updates(
    event_bus: PollEventBus = Depends(get_poll_event_bus),
):
    """
    Server-Sent Events endpoint for real-time poll updates.
    Broadcasts poll_created, poll_updated, and poll_deleted events.
    """
    async def event_generator():
        async for event in event_bus.subscribe():
            # Format: event_type and data fields for SSE
            yield {
                "event": event.event_type,
                "data": json.dumps(event.payload),
            }
    
    return EventSourceResponse(event_generator())

