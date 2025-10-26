"""In-memory event bus for broadcasting poll updates to SSE subscribers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, Set

from ..schemas.poll import Poll as PollSchema


@dataclass
class PollEvent:
    """Represents a poll update event."""

    event_type: str
    payload: Dict[str, Any]


class PollEventBus:
    """A simple in-memory pub/sub bus for poll events."""

    def __init__(self, *, max_queue_size: int = 100) -> None:
        self._subscribers: Set[asyncio.Queue[PollEvent]] = set()
        self._max_queue_size = max_queue_size
        self._lock = asyncio.Lock()

    async def publish(self, event: PollEvent) -> None:
        """Publish an event to all subscribers."""

        async with self._lock:
            queues_snapshot = list(self._subscribers)

        for queue in queues_snapshot:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                # Drop the oldest event to make room for new ones
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                finally:
                    queue.put_nowait(event)

    async def subscribe(self) -> AsyncIterator[PollEvent]:
        """Subscribe to event stream as an async iterator."""

        queue: asyncio.Queue[PollEvent] = asyncio.Queue(maxsize=self._max_queue_size)

        async with self._lock:
            self._subscribers.add(queue)

        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            async with self._lock:
                self._subscribers.discard(queue)


def build_poll_event(event_type: str, poll_model: Any) -> PollEvent:
    """Create a PollEvent from a SQLAlchemy poll model."""

    poll_payload = PollSchema.from_orm(poll_model).model_dump(mode='json')
    return PollEvent(event_type=event_type, payload={"poll": poll_payload})


