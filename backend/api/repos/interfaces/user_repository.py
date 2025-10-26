
from abc import ABC, abstractmethod
from typing import Optional
from ...schemas import user as user_schema
from ...models import users as user_model

class IUserRepository(ABC):
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[user_model.UserDB]:
        pass

    @abstractmethod
    async def create_user(self, user: user_schema.UserCreate, hashed_password: str) -> user_model.UserDB:
        pass
