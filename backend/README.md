  ## Polls API (Backend)

  FastAPI backend for a polls application with users, polls, likes/dislikes, and votes.

  ### Base URL
  - Local development: `http://localhost:8000/api`

  ### Authentication
  - JWT-based. Obtain a token via `POST /api/users/login`.
  - Use `Authorization: Bearer <token>` header for protected endpoints.

  ### Migrations (required before running)
  1) Ensure `DATABASE_URL` is set (e.g., in `.env`).
  2) Autogenerate migration for new tables (if not already generated):
    - `poetry run alembic revision --autogenerate -m "add polls and votes"`
  3) Apply migrations:
    - `poetry run alembic upgrade head`

  ### Run the server
  - `poetry run uvicorn main:app --reload`

  ---

  ## Users Endpoints

  ### Create user
  - POST `/api/users/`
  - Body:
  ```json
  {
    "email": "user@test.com",
    "full_name": "Test User",
    "password": "secret123"
  }
  ```
  - 201 → Returns created user

  ### Login (simple JSON body)
  - POST `/api/users/login`
  - Body:
  ```json
  {
    "email": "user@test.com",
    "password": "secret123"
  }
  ```
  - 200 → `{ access_token, token_type, expires_in, user }`

  ### Current user
  - GET `/api/users/me` (requires Bearer token)

  ### Admin check
  - GET `/api/users/admin/me` (requires admin user)

  ### Logout (client-side)
  - POST `/api/users/logout`

  ### Refresh token
  - POST `/api/users/refresh` (requires Bearer token)

  ### Validate token
  - GET `/api/users/validate-token` (requires Bearer token)

  ---

  ## Polls Endpoints

  ### Create poll
  - POST `/api/polls/` (requires Bearer token)
  - Body:
  ```json
  {
    "title": "What's your favorite search engine?",
    "description": "Vote now",
    "poll_expires_at": "2025-11-02T12:00:00Z",
    "options": [
      { "text": "Google" },
      { "text": "DuckDuckGo" },
      { "text": "Brave" },
      { "text": "Bing" }
    ]
  }
  ```
  - 201 → Returns the created poll with:
    - `creator`, `options`, `liked_by`, `disliked_by` eagerly loaded

  Curl example:
  ```bash
  curl -X POST http://localhost:8000/api/polls/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "title":"What\'s your favorite search engine?",
      "description":"Vote now",
      "poll_expires_at":"2025-11-02T12:00:00Z",
      "options":[{"text":"Google"},{"text":"DuckDuckGo"},{"text":"Brave"},{"text":"Bing"}]
    }'
  ```

  ### List polls (ranked)
  - POST `/api/polls/list`
  - Body:
  ```json
  { "sort_by": "created_at", "limit": 50, "offset": 0 }
  ```
  - `sort_by`: `"created_at"` or `"likes"`
  - 200 → Array of polls with `creator`, `options`, `liked_by`, `disliked_by`
  - If a Bearer token is provided, each poll includes `my_vote_option_id` indicating the current user's chosen option (or `null` if not voted)

  ### List my polls
  - POST `/api/polls/mine` (requires Bearer token)
  - Body same as list:
  ```json
  { "sort_by": "created_at", "limit": 50, "offset": 0 }
  ```
  - 200 → Array of polls created by current user
  - Response includes `my_vote_option_id` for the current user when present

  ### Delete poll
  - DELETE `/api/polls/{poll_id}` (requires Bearer token)
  - Only the creator or an admin can delete
  - 204 → No content

  ### Like a poll
  - POST `/api/polls/{poll_id}/like` (requires Bearer token)
  - 200 → Returns the updated poll with synchronized `likes`/`dislikes` counts

  Curl example:
  ```bash
  curl -X POST http://localhost:8000/api/polls/1/like \
    -H "Authorization: Bearer $TOKEN"
  ```

  ### Dislike a poll
  - POST `/api/polls/{poll_id}/dislike` (requires Bearer token)
  - 200 → Returns the updated poll with synchronized `likes`/`dislikes` counts

  Curl example:
  ```bash
  curl -X POST http://localhost:8000/api/polls/1/dislike \
    -H "Authorization: Bearer $TOKEN"
  ```

  ### Real-time Poll Updates (SSE)
  - GET `/api/polls/stream`
  - Server-Sent Events endpoint for real-time poll updates
  - No authentication required (public data broadcast)
  - Events:
    - `poll_created`: New poll created
    - `poll_updated`: Poll stats changed (likes, dislikes, votes)
    - `poll_deleted`: Poll deleted
  - Each event includes the full poll object (except `poll_deleted` which only sends `poll_id`)

  Example usage in JavaScript:
  ```javascript
  const eventSource = new EventSource('http://localhost:8000/api/polls/stream');

  eventSource.addEventListener('poll_updated', (event) => {
      const data = JSON.parse(event.data);
      console.log('Poll updated:', data.poll);
      // Update poll in your UI
  });

  eventSource.addEventListener('poll_created', (event) => {
      const data = JSON.parse(event.data);
      console.log('New poll:', data.poll);
  });

  eventSource.addEventListener('poll_deleted', (event) => {
      const data = JSON.parse(event.data);
      console.log('Poll deleted:', data.poll_id);
  });
  ```

  Testing with curl:
  ```bash
  curl -N http://localhost:8000/api/polls/stream
  ```

  **Note**: Use this for real-time updates to vote counts, likes/dislikes. For the full poll list, continue using short polling (POST `/api/polls/list` every ~1 minute).

  ---

  ## Votes Endpoints

  ### Cast vote
  - POST `/api/votes` (requires Bearer token)
  - Body:
  ```json
  { "poll_id": 1, "option_id": 2 }
  ```
  - Behavior: Upsert — if the user already voted on the poll, their selected option is updated.
  - 201 → Returns the user's vote

  Curl example:
  ```bash
  curl -X POST http://localhost:8000/api/votes \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"poll_id":1, "option_id":2}'
  ```

  ---

  ## Data Models (response highlights)

  ### Poll
  ```json
  {
    "id": 1,
    "title": "string",
    "description": "string|null",
    "likes": 0,
    "dislikes": 0,
    "created_at": "ISO-8601",
    "updated_at": "ISO-8601|null",
    "created_by": 1,
    "creator": { "id": 1, "email": "user@test.com", "full_name": "string", "is_admin": false, "created_at": "ISO-8601" },
    "options": [ { "id": 1, "text": "Google", "votes": 0 } ],
    "liked_by": [ { "id": 2, "email": "a@b.com", ... } ],
    "disliked_by": [],
    "my_vote_option_id": 2
  }
  ```

  ### Vote
  ```json
  {
    "id": 10,
    "user_id": 1,
    "poll_id": 1,
    "option_id": 2,
    "created_at": "ISO-8601"
  }
  ```

  ### Common Errors
  - 400 Bad Request: validation failed (e.g., options must be `[ { "text": "..." } ]`)
  - 401 Unauthorized: missing/invalid token
  - 403 Forbidden: not allowed (e.g., deleting someone else’s poll)
  - 404 Not Found: resource missing

  ---

  ## Notes
  - The API eagerly loads related data to avoid async lazy-load issues when serializing responses.
  - Likes/dislikes are many-to-many and counts are synchronized from association tables when liking/disliking.
  - Poll listings accept optional Bearer auth; when present, the server enriches each poll with `my_vote_option_id` using a single bulk lookup to avoid N+1 queries.


