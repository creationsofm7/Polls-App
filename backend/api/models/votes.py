from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Vote(Base):
    __tablename__ = "poll_votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False, index=True)
    option_id = Column(Integer, ForeignKey("poll_options.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "poll_id", name="uq_poll_vote_user_per_poll"),
    )

    user = relationship("UserDB", back_populates="votes")
    poll = relationship("Poll", back_populates="votes")
    option = relationship("PollOption", back_populates="votes_rel")

