from datetime import datetime
from pydantic import BaseModel


class VoteCreate(BaseModel):
    poll_id: int
    option_id: int


class Vote(BaseModel):
    id: int
    user_id: int
    poll_id: int
    option_id: int
    created_at: datetime

    class Config:
        from_attributes = True

