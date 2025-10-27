from fastapi import APIRouter, Depends, status
from ..dependencies import get_vote_service
from ..services.vote_service import VoteService
from ..auth import get_current_user_simple
from ..schemas.vote import VoteCreate
from ..schemas.poll import Poll
from ..schemas.user import User


router = APIRouter(prefix="/votes", tags=["Votes"])


@router.post("/", response_model=Poll, status_code=status.HTTP_201_CREATED)
async def cast_vote(
    payload: VoteCreate,
    current_user: User = Depends(get_current_user_simple),
    vote_service: VoteService = Depends(get_vote_service),
):
    return await vote_service.cast_vote(user_id=current_user.id, payload=payload)


