from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

# Association tables for many-to-many relationships
poll_likes = Table(
    'poll_likes',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('poll_id', Integer, ForeignKey('polls.id'), primary_key=True)
)

poll_dislikes = Table(
    'poll_dislikes',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('poll_id', Integer, ForeignKey('polls.id'), primary_key=True)
)


class Poll(Base):
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    poll_expires_at = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    options = relationship("PollOption", back_populates="poll", cascade="all, delete-orphan")
    creator = relationship("UserDB", back_populates="created_polls")
    liked_by = relationship("UserDB", secondary=poll_likes, back_populates="liked_polls")
    disliked_by = relationship("UserDB", secondary=poll_dislikes, back_populates="disliked_polls")
    votes = relationship("Vote", back_populates="poll", cascade="all, delete-orphan")
    
    


class PollOption(Base):
    __tablename__ = "poll_options"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    votes = Column(Integer, default=0, nullable=False)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)
    
    # Relationships
    poll = relationship("Poll", back_populates="options")
    votes_rel = relationship("Vote", back_populates="option", cascade="all, delete-orphan")


    
    