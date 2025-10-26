from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from .user import User


class PollOptionBase(BaseModel):
    text: str


class PollOptionCreate(PollOptionBase):
    pass


class PollOption(PollOptionBase):
    id: int
    votes: int = 0

    class Config:
        from_attributes = True


class PollBase(BaseModel):
    title: str
    description: Optional[str] = None
    poll_expires_at: Optional[datetime] = None


class PollCreate(PollBase):
    options: List[PollOptionCreate]


class Poll(PollBase):
    id: int
    likes: int
    dislikes: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    options: List[PollOption]
    creator: Optional[User] = None
    liked_by: List[User] = Field(default_factory=list)
    disliked_by: List[User] = Field(default_factory=list)
    my_vote_option_id: Optional[int] = None

    class Config:
        from_attributes = True

