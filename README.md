# 🗳️ Polls - Interactive Polling Platform

A modern, full-stack polling application that enables users to create, share, and participate in polls with real-time results and community engagement features.

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
