
from typing import Optional
from anyio import to_thread
from ..repos.interfaces.user_repository import IUserRepository
from ..schemas import user as user_schema
from ..models import users as user_model
 
from ..exceptions import ConflictException

class UserService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        from ..auth import AuthService
        self.auth_service = AuthService(user_repository)

    async def create_user(self, user: user_schema.UserCreate) -> user_model.UserDB:
        db_user = await self.user_repository.get_user_by_email(email=user.email)
        if db_user:
            raise ConflictException(detail="Email already registered")

        hashed_password = await to_thread.run_sync(self.auth_service.get_password_hash, user.password)
        return await self.user_repository.create_user(user=user, hashed_password=hashed_password)

    async def authenticate_user(self, email: str, password: str) -> Optional[user_model.UserDB]:
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            return None
        valid = await to_thread.run_sync(self.auth_service.verify_password, password, user.hashed_password)
        if not valid:
            return None
        return user

    def create_access_token(self, data: dict) -> str:
        return self.auth_service.create_access_token(data=data)
