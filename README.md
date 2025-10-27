# 🗳️ Polls - Interactive Polling Platform

A modern, full-stack polling application that enables users to create, share, and participate in polls with real-time results and community engagement features.

🌐 **Live Demo**: [https://polls-app-nu.vercel.app/](https://polls-app-nu.vercel.app/)

## 🧪 Try It Out

Test the real-time sync behavior with these demo accounts:

| Email | Password | Purpose |
|-------|----------|---------|
| `user@test.com` | `123456` | Primary test account |
| `comet@comet.com` | `123456` | Secondary account for testing sync |

**How to test real-time features:**
1. Open the app in two different browser tabs/windows
2. Sign in with different accounts in each tab
3. Create a poll in one tab and watch it appear instantly in the other
4. Cast votes and see live updates across all connected clients
5. Like/dislike polls to see real-time community engagement

![Polls Platform](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.117.1-green?style=for-the-badge&logo=fastapi)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?style=for-the-badge&logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge&logo=postgresql)

## ✨ Features

### 🎯 Core Functionality
- **Create Custom Polls**: Design polls with multiple options, descriptions, and expiration dates
- **Real-time Voting**: Cast votes and see live results with percentage breakdowns
- **Interactive Results**: Visual progress bars and detailed statistics
- **Community Engagement**: Like/dislike polls and track community sentiment

### 🔐 User Management
- **Secure Authentication**: JWT-based authentication with refresh tokens
- **User Profiles**: Personal dashboards to manage created polls
- **Role-based Access**: Admin capabilities for platform management

### 🎨 User Experience
- **Responsive Design**: Mobile-first interface that works on all devices
- **Dark Mode Support**: Beautiful dark theme with smooth transitions
- **Real-time Updates**: Server-Sent Events for live poll updates
- **Professional UI**: Clean, modern design with intuitive navigation

## 🏗️ Architecture

This is a monorepo containing both frontend and backend applications:

```
polls/
├── backend/                 # FastAPI backend application
│   ├── api/                # API layer with routers, models, services
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   └── main.py             # Application entry point
├── frontend/               # Next.js frontend application
│   ├── app/                # Next.js app directory
│   ├── components/         # React components
│   ├── lib/                # Utility libraries and API client
│   └── stores/             # State management
├── docker-compose.yml      # Local development setup
└── package.json            # Monorepo management
```

## 🚧 Challenges Faced and Solutions

This section documents the key technical challenges encountered during development and the solutions implemented to address them.

### 🔄 Real-time Updates with Server-Sent Events (SSE)

**Challenge**: Implementing real-time poll updates without complex WebSocket infrastructure.

**Solution**: Leveraged Server-Sent Events using Starlette's `EventSourceResponse` for efficient one-way communication from server to client.

**Implementation**:
- **Backend**: Custom `PollEventBus` class manages in-memory pub/sub system with asyncio queues
- **Event Types**: `poll_created`, `poll_updated`, `poll_deleted` events broadcast to all connected clients
- **Frontend**: Native `EventSource` API connects to `/api/polls/stream` endpoint
- **Reference**: Inspired by [FastAPI SSE implementation guide](https://medium.com/@Rachita_B/implementing-sse-server-side-events-using-fastapi-3b2d6768249e)

```python
# Backend SSE endpoint
@router.get("/stream")
async def stream_poll_updates(event_bus: PollEventBus = Depends(get_poll_event_bus)):
    async def event_generator():
        async for event in event_bus.subscribe():
            yield {"event": event.event_type, "data": json.dumps(event.payload)}
    return EventSourceResponse(event_generator())
``` 

### ⚡ Optimistic UI with React's useOptimistic Hook

**Challenge**: Providing immediate user feedback while maintaining data consistency.

**Solution**: Implemented React 18's `useOptimistic` hook for instant UI updates with automatic rollback on errors.

**Implementation**:
- **Vote Casting**: Immediate vote count updates with optimistic state management
- **Like/Dislike**: Instant UI feedback with proper state synchronization
- **Error Handling**: Automatic rollback to server state on API failures
- **Reference**: Following [React's useOptimistic documentation](https://react.dev/reference/react/useOptimistic)

```typescript
// Optimistic vote casting with automatic rollback
const [optimisticPoll, dispatchOptimisticPoll] = useOptimistic(poll, optimisticPollReducer);

const handleVote = useCallback(async (optionId: number) => {
  startTransition(async () => {
    dispatchOptimisticPoll({ type: "vote", optionId }); // Immediate UI update
    try {
      const updatedPoll = await castVote(payload, token);
      onUpdated?.(updatedPoll); // Sync with server state
    } catch (err) {
      // Automatic rollback handled by useOptimistic
    }
  });
}, []);
```

### 🎨 Responsive Design with shadcn/ui

**Challenge**: Creating a consistent, accessible, and responsive user interface across all devices.

**Solution**: Adopted shadcn/ui component library with Tailwind CSS for modern, mobile-first design.

**Implementation**:
- **Component Library**: Pre-built accessible components with consistent styling
- **Mobile Navigation**: Bottom navigation bar appears on mobile devices (`lg:hidden`)
- **Desktop Sidebar**: Sticky sidebar navigation for larger screens (`hidden lg:block`)
- **Responsive Layout**: Flexible grid system adapting to different screen sizes
- **Dark Mode**: Built-in dark mode support with CSS variables

```tsx
// Responsive navigation implementation
<aside className="hidden lg:block lg:w-64 lg:flex-shrink-0">
  {/* Desktop sidebar */}
</aside>

<nav className="fixed bottom-0 left-0 right-0 z-20 lg:hidden">
  {/* Mobile bottom navigation */}
</nav>
```

### 🔄 Asynchronous Operations with asyncio

**Challenge**: Managing concurrent database operations and real-time event processing efficiently.

**Solution**: Comprehensive use of Python's asyncio for non-blocking operations throughout the application.

**Implementation**:
- **Database Operations**: All repository methods use async/await patterns
- **Event Broadcasting**: Asynchronous event publishing and subscription
- **Rate Limiting**: Async-compatible rate limiting with asyncio locks
- **Password Hashing**: Non-blocking password operations using `anyio.to_thread`

```python
# Asynchronous event bus with asyncio
class PollEventBus:
    def __init__(self, *, max_queue_size: int = 100):
        self._subscribers: Set[asyncio.Queue[PollEvent]] = set()
        self._lock = asyncio.Lock()
    
    async def publish(self, event: PollEvent) -> None:
        async with self._lock:
            queues_snapshot = list(self._subscribers)
        # Async event distribution...
```

### 🏗️ Dependency Injection for Loose Coupling

**Challenge**: Maintaining clean architecture with testable, loosely coupled components.

**Solution**: Implemented a custom dependency injection container with singleton pattern and FastAPI integration.

**Implementation**:
- **Centralized Container**: `DependencyContainer` manages all service and repository instances
- **Singleton Pattern**: Services cached by class name, repositories by session ID
- **FastAPI Integration**: Dependency providers automatically inject dependencies
- **Testability**: `temporary_override` context manager for easy testing

```python
# Dependency injection with automatic resolution
def get_poll_service(
    poll_repo: IPollRepository = Depends(get_poll_repository),
    event_bus: PollEventBus = Depends(get_poll_event_bus)
) -> PollService:
    container = get_container()
    return container.get_service(PollService, poll_repository=poll_repo, event_bus=event_bus)
```

### 🗄️ PostgreSQL with asyncpg for High Performance

**Challenge**: Efficient database operations with connection pooling and async support.

**Solution**: Used asyncpg driver with SQLAlchemy's async engine for optimal PostgreSQL performance.

**Implementation**:
- **Async Driver**: asyncpg provides native async PostgreSQL support
- **Connection Pooling**: NullPool for serverless environments (Railway/Neon)
- **Statement Caching**: Disabled for serverless compatibility
- **Migration Support**: Alembic with async URL conversion

```python
# Async PostgreSQL configuration
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    poolclass=pool.NullPool,  # Serverless-optimized
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }
)
```

### 📱 Mobile-First Responsive Design

**Challenge**: Ensuring optimal user experience across all device sizes.

**Solution**: Mobile-first approach with progressive enhancement for larger screens.

**Implementation**:
- **Breakpoint Strategy**: `sm:`, `md:`, `lg:` prefixes for responsive behavior
- **Navigation Adaptation**: Bottom nav on mobile, sidebar on desktop
- **Touch-Friendly**: Larger touch targets and appropriate spacing
- **Performance**: Optimized images and lazy loading

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and **pnpm** 8+
- **Python** 3.13+ and **Poetry**
- **PostgreSQL** database

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd polls

# Install root dependencies
npm install

# Install backend dependencies
cd backend && poetry install

# Install frontend dependencies
cd frontend && pnpm install
```

### 2. Environment Configuration

Create environment files:

```bash
# Backend environment
cp env.example backend/.env

# Frontend environment (if needed)
cp env.example frontend/.env.local
```

Configure your database URL in `backend/.env`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/polls_db
```

### 3. Database Setup

```bash
cd backend

# Run database migrations
poetry run alembic upgrade head
```

### 4. Start Development Servers

```bash
# Start both backend and frontend concurrently
npm run dev

# Or start individually:
npm run dev:backend   # Backend: http://localhost:8000
npm run dev:frontend  # Frontend: http://localhost:3000
```

## 📚 API Documentation

The backend provides comprehensive API documentation:

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **API Reference**: See [backend/README.md](backend/README.md) for detailed endpoint documentation

### Key Endpoints

- `POST /api/users/` - Create user account
- `POST /api/users/login` - User authentication
- `POST /api/polls/` - Create new poll
- `POST /api/polls/list` - Get polls with sorting/filtering
- `POST /api/votes` - Cast vote on poll
- `GET /api/polls/stream` - Real-time poll updates (SSE)

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Alembic** - Database migration tool
- **PostgreSQL** - Robust relational database
- **JWT** - Secure token-based authentication
- **Poetry** - Dependency management and packaging

### Frontend
- **Next.js 16** - React framework with App Router
- **React 19** - Latest React with concurrent features
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - Lightweight state management
- **React Query** - Server state management
- **Radix UI** - Accessible component primitives
- **React Hook Form** - Performant forms with validation

## 📦 Available Scripts

### Development
```bash
npm run dev              # Start both servers
npm run dev:backend      # Backend only
npm run dev:frontend     # Frontend only
```

### Building
```bash
npm run build            # Build both applications
npm run build:backend    # Backend only
npm run build:frontend   # Frontend only
```

### Testing
```bash
npm run test             # Run all tests
npm run test:backend     # Backend tests only
npm run test:frontend    # Frontend tests only
```

### Code Quality
```bash
npm run lint             # Lint both applications
npm run format           # Format code
```

## 🚀 Deployment

### Backend Deployment
The FastAPI backend can be deployed to any Python hosting service:

- **Railway**: Connect GitHub repo for automatic deployments
- **Render**: Deploy with Docker or direct Python deployment
- **Heroku**: Use the included `Procfile`
- **DigitalOcean App Platform**: Direct deployment from GitHub

### Frontend Deployment
The Next.js frontend is optimized for static deployment:

- **Vercel**: Recommended - automatic deployments from GitHub
- **Netlify**: Static site deployment with edge functions
- **AWS S3 + CloudFront**: Static hosting with CDN

### Environment Variables

**Backend** (`.env`):
```env
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
HOST=0.0.0.0
PORT=8000
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
```

## 🧪 Testing

The application includes comprehensive testing:

- **Backend**: pytest with async support
- **Frontend**: Jest with React Testing Library
- **E2E**: Integration tests for critical user flows

Run tests:
```bash
npm run test
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes
4. **Test** thoroughly: `npm run test`
5. **Lint** your code: `npm run lint`
6. **Commit** your changes: `git commit -m 'Add amazing feature'`
7. **Push** to the branch: `git push origin feature/amazing-feature`
8. **Open** a Pull Request

### Development Guidelines

- Follow the existing code style and patterns
- Write tests for new features
- Update documentation as needed
- Use conventional commit messages
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern web technologies and best practices
- Inspired by community-driven polling platforms
- Thanks to all contributors and the open-source community

---

**Happy Polling!** 🗳️✨
