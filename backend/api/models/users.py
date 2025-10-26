
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_polls = relationship("Poll", back_populates="creator")
    liked_polls = relationship("Poll", secondary="poll_likes", back_populates="liked_by")
    disliked_polls = relationship("Poll", secondary="poll_dislikes", back_populates="disliked_by")
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")
