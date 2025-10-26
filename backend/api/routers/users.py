
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from ..dependencies import get_user_service
from ..services.user_service import UserService
from ..auth import get_current_user, get_current_admin_user, get_current_user_simple
from ..schemas import user as user_schema
from ..schemas import token as token_schema
from ..exceptions import ConflictException
from ..config import settings
from ..utils.rate_limiting import rate_limit
import time

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: user_schema.UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.create_user(user=user)
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.post("/login", response_model=token_schema.LoginResponse)
@rate_limit(max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes
async def login_for_access_token(
    login_data: token_schema.LoginRequest,
    request: Request,
    user_service: UserService = Depends(get_user_service)
):
    """
    Login with email and password to get JWT token.
    
    - **email**: Your registered email address
    - **password**: Your password (minimum 6 characters)
    
    Returns a JWT token and user information.
    """
    user = await user_service.authenticate_user(email=login_data.email, password=login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials and try again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = user_service.create_access_token(data={"sub": user.email})
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat()
        }
    }

@router.post("/login/oauth2", response_model=token_schema.Token)
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    """
    OAuth2 compatible login endpoint (for compatibility with OAuth2PasswordRequestForm).
    
    This endpoint maintains compatibility with OAuth2 standards.
    """
    user = await user_service.authenticate_user(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = user_service.create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": user.id,
        "user_email": user.email
    }

@router.get("/me", response_model=user_schema.User)
async def read_users_me(current_user: user_schema.User = Depends(get_current_user_simple)):
    """
    Get current user profile using Bearer token.
    
    Simply paste your JWT token in the Authorization field.
    """
    return current_user

@router.get("/admin/me", response_model=user_schema.User)
async def read_admin_me(current_user: user_schema.User = Depends(get_current_admin_user)):
    """An example of a protected route that requires admin privileges."""
    return current_user

@router.post("/logout")
def logout():
    """
    Logout endpoint (client-side token invalidation).
    
    Note: JWT tokens are stateless, so actual invalidation happens client-side.
    This endpoint provides a standard logout interface.
    """
    return {
        "message": "Successfully logged out. Please remove the token from your client.",
        "logout_time": time.time()
    }

@router.post("/refresh", response_model=token_schema.LoginResponse)
async def refresh_token(
    current_user: user_schema.User = Depends(get_current_user_simple),
    user_service: UserService = Depends(get_user_service)
):
    """
    Refresh JWT token for authenticated users.
    
    Returns a new JWT token with extended expiration.
    """
    access_token = user_service.create_access_token(data={"sub": current_user.email})
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_admin": current_user.is_admin,
            "created_at": current_user.created_at.isoformat()
        }
    }

@router.get("/validate-token")
async def validate_token(current_user: user_schema.User = Depends(get_current_user_simple)):
    """
    Validate if your JWT token is still valid.
    
    Simply paste your JWT token in the Authorization field.
    Returns user info if token is valid.
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_admin": current_user.is_admin
        }
    }
