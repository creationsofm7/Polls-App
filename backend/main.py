
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from api.routers import users, polls
from api.routers import votes as votes_router
import uvicorn
from api.config import settings, setup_logging
from api.middlewares import setup_middleware
from api.database import close_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    yield
    # Shutdown
    await close_db_connection()

app = FastAPI(
    title=settings.APP_NAME,
    description="A production-ready FastAPI project with Clean Architecture.",
    version="1.0.0",
    lifespan=lifespan
)

# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(users.router, prefix="/api")
app.include_router(polls.router, prefix="/api")
app.include_router(votes_router.router, prefix="/api")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )