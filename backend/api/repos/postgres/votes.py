from typing import Optional, List, Dict
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..interfaces.vote_repository import IVoteRepository
from ...schemas.vote import VoteCreate
from ...models.votes import Vote
from ...models.polls import PollOption


class PostgresVoteRepository(IVoteRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def cast_vote(self, user_id: int, payload: VoteCreate) -> Vote:
        # Ensure option belongs to poll
        option = await self.db.get(PollOption, payload.option_id)
        if not option or option.poll_id != payload.poll_id:
            raise ValueError("Option does not belong to poll")

        # Upsert: one vote per user per poll
        existing = await self.get_user_vote_for_poll(user_id, payload.poll_id)
        if existing:
            old_option_id = existing.option_id
            if old_option_id == payload.option_id:
                await self.db.flush()
                await self.db.refresh(existing)
                return existing
            existing.option_id = payload.option_id
            # Flush changes so sync counts see the new value
            await self.db.flush()
            await self._sync_option_vote_counts([old_option_id, payload.option_id])
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        vote = Vote(user_id=user_id, poll_id=payload.poll_id, option_id=payload.option_id)
        self.db.add(vote)
        # Flush so the new row is visible to the following count query
        await self.db.flush()
        await self._sync_option_vote_counts([payload.option_id])
        await self.db.commit()
        await self.db.refresh(vote)
        return vote

    async def get_user_vote_for_poll(self, user_id: int, poll_id: int) -> Optional[Vote]:
        result = await self.db.execute(
            select(Vote).where((Vote.user_id == user_id) & (Vote.poll_id == poll_id))
        )
        return result.scalars().first()

    async def list_user_votes_for_polls(self, user_id: int, poll_ids: List[int]) -> Dict[int, int]:
        if not poll_ids:
            return {}
        result = await self.db.execute(
            select(Vote.poll_id, Vote.option_id).where(
                (Vote.user_id == user_id) & (Vote.poll_id.in_(poll_ids))
            )
        )
        rows = result.all()
        return {poll_id: option_id for poll_id, option_id in rows}

    async def _sync_option_vote_counts(self, option_ids: List[int]) -> None:
        if not option_ids:
            return
        # Count current votes per option
        count_rows = await self.db.execute(
            select(Vote.option_id, func.count())
            .where(Vote.option_id.in_(option_ids))
            .group_by(Vote.option_id)
        )
        counts: Dict[int, int] = {oid: 0 for oid in option_ids}
        for oid, cnt in count_rows.all():
            counts[oid] = cnt
        # Update each option's votes to the exact count
        for oid, cnt in counts.items():
            await self.db.execute(
                update(PollOption).where(PollOption.id == oid).values(votes=cnt)
            )

