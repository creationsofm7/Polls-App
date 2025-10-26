from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from ..interfaces.poll_repository import IPollRepository
from ...models.polls import Poll, PollOption
from ...models.polls import poll_likes, poll_dislikes
from ...schemas.poll import PollCreate


class PostgresPollRepository(IPollRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_poll(self, user_id: int, payload: PollCreate) -> Poll:
        poll = Poll(
            title=payload.title,
            description=payload.description,
            poll_expires_at=payload.poll_expires_at,
            created_by=user_id,
        )
        for opt in payload.options:
            poll.options.append(PollOption(text=opt.text, votes=0))

        self.db.add(poll)
        await self.db.flush()
        await self.db.commit()

        # Reload with relationships eagerly loaded to prevent async lazy-load during response serialization
        stmt = (
            select(Poll)
            .where(Poll.id == poll.id)
            .options(
                selectinload(Poll.creator),
                selectinload(Poll.options),
                selectinload(Poll.liked_by),
                selectinload(Poll.disliked_by),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().unique().first()

    async def get_poll(self, poll_id: int) -> Optional[Poll]:
        result = await self.db.execute(select(Poll).where(Poll.id == poll_id))
        return result.scalars().first()

    async def list_polls(self, *, limit: int = 50, offset: int = 0) -> List[Poll]:
        result = await self.db.execute(select(Poll).offset(offset).limit(limit))
        return result.scalars().all()

    async def list_polls_detailed(self, *, sort_by: str = "created_at", limit: int = 50, offset: int = 0) -> List[Poll]:
        order_col = Poll.created_at if sort_by == "created_at" else Poll.likes
        stmt = (
            select(Poll)
            .options(
                selectinload(Poll.creator),
                selectinload(Poll.options),
                selectinload(Poll.liked_by),
                selectinload(Poll.disliked_by),
            )
            .order_by(order_col.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().unique().all()

    async def list_polls_by_user_detailed(self, user_id: int, *, sort_by: str = "created_at", limit: int = 50, offset: int = 0) -> List[Poll]:
        order_col = Poll.created_at if sort_by == "created_at" else Poll.likes
        stmt = (
            select(Poll)
            .where(Poll.created_by == user_id)
            .options(
                selectinload(Poll.creator),
                selectinload(Poll.options),
                selectinload(Poll.liked_by),
                selectinload(Poll.disliked_by),
            )
            .order_by(order_col.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().unique().all()

    async def get_poll_with_users(self, poll_id: int) -> Optional[Poll]:
        stmt = (
            select(Poll)
            .where(Poll.id == poll_id)
            .options(
                selectinload(Poll.creator),
                selectinload(Poll.options),
                selectinload(Poll.liked_by),
                selectinload(Poll.disliked_by),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().unique().first()

    async def like_poll(self, poll_id: int, user_id: int) -> Poll:
        # Lock the poll row to prevent concurrent counter updates
        lock_stmt = select(Poll).where(Poll.id == poll_id).with_for_update()
        lock_result = await self.db.execute(lock_stmt)
        poll = lock_result.scalars().first()
        if not poll:
            raise ValueError("Poll not found")

        # remove dislike if present
        await self.db.execute(
            poll_dislikes.delete().where(
                (poll_dislikes.c.user_id == user_id) & (poll_dislikes.c.poll_id == poll_id)
            )
        )

        # insert like if not exists
        existing_like = await self.db.execute(
            select(poll_likes).where(
                (poll_likes.c.user_id == user_id) & (poll_likes.c.poll_id == poll_id)
            )
        )
        if existing_like.first() is None:
            await self.db.execute(
                poll_likes.insert().values(user_id=user_id, poll_id=poll_id)
            )

        # synchronize counters atomically based on association tables
        likes_count_result = await self.db.execute(
            select(func.count()).select_from(poll_likes).where(poll_likes.c.poll_id == poll_id)
        )
        dislikes_count_result = await self.db.execute(
            select(func.count()).select_from(poll_dislikes).where(poll_dislikes.c.poll_id == poll_id)
        )
        poll.likes = likes_count_result.scalar_one()
        poll.dislikes = dislikes_count_result.scalar_one()
        
        await self.db.commit()

        # Return with relationships eagerly loaded to avoid async lazy-load during serialization
        return await self.get_poll_with_users(poll_id)

    async def dislike_poll(self, poll_id: int, user_id: int) -> Poll:
        # Lock the poll row to prevent concurrent counter updates
        lock_stmt = select(Poll).where(Poll.id == poll_id).with_for_update()
        lock_result = await self.db.execute(lock_stmt)
        poll = lock_result.scalars().first()
        if not poll:
            raise ValueError("Poll not found")

        # remove like if present
        await self.db.execute(
            poll_likes.delete().where(
                (poll_likes.c.user_id == user_id) & (poll_likes.c.poll_id == poll_id)
            )
        )

        # insert dislike if not exists
        existing_dislike = await self.db.execute(
            select(poll_dislikes).where(
                (poll_dislikes.c.user_id == user_id) & (poll_dislikes.c.poll_id == poll_id)
            )
        )
        if existing_dislike.first() is None:
            await self.db.execute(
                poll_dislikes.insert().values(user_id=user_id, poll_id=poll_id)
            )

        # synchronize counters atomically based on association tables
        likes_count_result = await self.db.execute(
            select(func.count()).select_from(poll_likes).where(poll_likes.c.poll_id == poll_id)
        )
        dislikes_count_result = await self.db.execute(
            select(func.count()).select_from(poll_dislikes).where(poll_dislikes.c.poll_id == poll_id)
        )
        poll.likes = likes_count_result.scalar_one()
        poll.dislikes = dislikes_count_result.scalar_one()
        
        await self.db.commit()

        # Return with relationships eagerly loaded to avoid async lazy-load during serialization
        return await self.get_poll_with_users(poll_id)

    async def delete_poll(self, poll_id: int) -> None:
        poll = await self.get_poll(poll_id)
        if not poll:
            return
        await self.db.delete(poll)
        await self.db.commit()

