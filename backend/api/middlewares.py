
import time
import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

log = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address)

def setup_middleware(app: FastAPI):
    # Apply rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next) -> Response:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            path=request.url.path,
            method=request.method,
            client_host=request.client.host
        )
        start_time = time.time()

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        log.info(
            "Request completed",
            status_code=response.status_code,
            duration_ms=round(process_time, 2),
        )
        return response

    # CORS Middleware (should be one of the first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Or specify your front-end domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add other middleware like security headers here
