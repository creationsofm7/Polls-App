from functools import wraps
from typing import Dict
import time
import asyncio
from fastapi import HTTPException, Request, status


def _extract_request(args):
    for arg in args:
        if isinstance(arg, Request):
            return arg
    return None

# Simple in-memory rate limiter (for production, use Redis)
class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key] 
            if now - req_time < window_seconds
        ]
        
        # Check if under the limit
        if len(self.requests[key]) >= max_requests:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    """
    Rate limiting decorator for endpoints.
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                request = _extract_request(args)
                if request:
                    client_ip = request.client.host
                    if not rate_limiter.is_allowed(client_ip, max_requests, window_seconds):
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Too many requests. Try again in {window_seconds} seconds."
                        )

                return await func(*args, **kwargs)

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            request = _extract_request(args)
            if request:
                client_ip = request.client.host
                if not rate_limiter.is_allowed(client_ip, max_requests, window_seconds):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Too many requests. Try again in {window_seconds} seconds."
                    )

            return func(*args, **kwargs)

        return sync_wrapper
    return decorator
