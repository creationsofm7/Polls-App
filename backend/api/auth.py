
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from .config import settings
from .repos.interfaces.user_repository import IUserRepository
from .schemas import user as user_schema
from .dependencies import get_user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

# Simple Bearer token scheme for easier use in docs
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()
bearer_scheme_optional = HTTPBearer(auto_error=False)

class AuthService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )

    def get_password_hash(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user_simple(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repo: IUserRepository = Depends(get_user_repository)
) -> user_schema.User:
    """Simple Bearer token authentication for easier docs usage"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_repo.get_user_by_email(email=email)
    if user is None:
        raise credentials_exception
    return user_schema.User.from_orm(user)

async def get_optional_user_simple(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme_optional),
    user_repo: IUserRepository = Depends(get_user_repository)
) -> Optional[user_schema.User]:
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    user = await user_repo.get_user_by_email(email=email)
    if user is None:
        return None
    return user_schema.User.from_orm(user)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: IUserRepository = Depends(get_user_repository)
) -> user_schema.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_repo.get_user_by_email(email=email)
    if user is None:
        raise credentials_exception
    return user_schema.User.from_orm(user)

async def get_current_admin_user(
    current_user: user_schema.User = Depends(get_current_user)
) -> user_schema.User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
