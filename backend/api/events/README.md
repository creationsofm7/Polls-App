# Poll Events System

This module implements a real-time event broadcasting system for poll updates using Server-Sent Events (SSE).

## Architecture

### Components

1. **PollEventBus** (`bus.py`)
   - In-memory pub/sub system for broadcasting poll events
   - Manages subscriber connections
   - Handles event distribution to all connected clients
   - Max queue size: 100 events per subscriber (configurable)

2. **PollEvent** (`bus.py`)
   - Dataclass representing a poll event
   - Contains `event_type` and `payload` fields

3. **Event Types**
   - `poll_created`: When a new poll is created
   - `poll_updated`: When poll stats change (likes, dislikes, votes)
   - `poll_deleted`: When a poll is deleted

### Integration Points

#### Services
- **PollService**: Emits events after create, like, dislike, delete operations
- **VoteService**: Emits poll_updated events when votes are cast

#### Dependencies
- `get_poll_event_bus()`: FastAPI dependency to inject the singleton event bus

#### Router
- `GET /polls/stream`: SSE endpoint for subscribing to real-time updates

## Usage

### Backend - Emitting Events

The event bus is automatically injected into services and events are emitted after successful operations:

```python
# In PollService
async def like_poll(self, poll_id: int, user_id: int) -> Poll:
    poll = await self.poll_repository.like_poll(poll_id=poll_id, user_id=user_id)
    if self.event_bus:
        event = build_poll_event("poll_updated", poll)
        await self.event_bus.publish(event)
    return poll
```

### Frontend - Subscribing to Events

Connect to the SSE endpoint to receive real-time updates:

```javascript
const eventSource = new EventSource('http://your-api/polls/stream');

eventSource.addEventListener('poll_created', (event) => {
    const data = JSON.parse(event.data);
    console.log('New poll created:', data.poll);
    // Update UI with new poll
});

eventSource.addEventListener('poll_updated', (event) => {
    const data = JSON.parse(event.data);
    console.log('Poll updated:', data.poll);
    // Update poll stats in UI (likes, dislikes, vote counts)
});

eventSource.addEventListener('poll_deleted', (event) => {
    const data = JSON.parse(event.data);
    console.log('Poll deleted:', data.poll_id);
    // Remove poll from UI
});

eventSource.onerror = (error) => {
    console.error('SSE connection error:', error);
    // Reconnect logic (EventSource auto-reconnects by default)
};
```

### Event Payloads

#### poll_created / poll_updated
```json
{
    "poll": {
        "id": 123,
        "title": "Favorite color?",
        "description": "Pick your favorite",
        "likes": 45,
        "dislikes": 3,
        "created_at": "2025-10-26T12:34:56Z",
        "created_by": 5,
        "options": [
            {"id": 1, "text": "Red", "votes": 120},
            {"id": 2, "text": "Blue", "votes": 169}
        ],
        "creator": {...},
        "liked_by": [...],
        "disliked_by": [...]
    }
}
```

#### poll_deleted
```json
{
    "poll_id": 123
}
```

## Design Decisions

### Why In-Memory?
- **Simplicity**: No external dependencies (Redis, RabbitMQ)
- **Low latency**: Direct memory access
- **Perfect for hobby projects**: Works great for single-instance deployments
- **Easy testing**: No infrastructure setup needed

### Limitations
- Only works with single backend instance
- Events lost on server restart (clients auto-reconnect)
- Not suitable for horizontally scaled deployments

### Scalability Path
If you need multi-instance support in the future:
1. Replace `PollEventBus` with Redis pub/sub
2. Keep the same interface (`publish()`, `subscribe()`)
3. No changes needed to services or routes

## Testing

To test the SSE endpoint:

```bash
# Start the server
poetry run uvicorn main:app --reload

# In another terminal, connect to SSE stream
curl -N http://localhost:8000/polls/stream

# In another terminal, trigger an event (e.g., like a poll)
curl -X POST http://localhost:8000/polls/1/like \
  -H "Authorization: Bearer YOUR_TOKEN"

# Watch the SSE stream receive the event
```

## Performance

- **Memory**: ~1KB per connected client (queue overhead)
- **Throughput**: Thousands of events/second on modern hardware
- **Connection limit**: Depends on system (typically ~10k concurrent SSE connections)
- **Queue overflow**: Old events are dropped if queue fills up

## Error Handling

- Client disconnections are handled gracefully
- Failed event delivery is silently dropped (fire-and-forget)
- Queue full: oldest event is dropped to make room for new one

