
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    """Login request schema with better field names and validation"""
    email: str = Field(..., description="User's email address", example="user@example.com")
    password: str = Field(..., min_length=6, description="User's password", example="password123")

class Token(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Token expiration time in seconds")
    user_id: Optional[int] = Field(None, description="User ID")
    user_email: Optional[str] = Field(None, description="User email")

class LoginResponse(BaseModel):
    """Enhanced login response with user information"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: dict = Field(..., description="User information")
