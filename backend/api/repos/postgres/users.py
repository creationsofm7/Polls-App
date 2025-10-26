
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..interfaces.user_repository import IUserRepository
from ...models.users import UserDB
from ...schemas.user import UserCreate

class PostgresUserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[UserDB]:
        result = await self.db.execute(select(UserDB).where(UserDB.email == email))
        return result.scalars().first()

    async def create_user(self, user: UserCreate, hashed_password: str) -> UserDB:
        # Make first user an admin for demonstration (best-effort, not strictly serialized)
        count_result = await self.db.execute(select(func.count(UserDB.id)))
        is_first_user = (count_result.scalar_one() == 0)

        db_user = UserDB(
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            is_admin=is_first_user
        )
        self.db.add(db_user)
        # Ensure PK/defaults available
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
