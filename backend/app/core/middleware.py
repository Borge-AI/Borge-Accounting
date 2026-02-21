"""
Custom middleware.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to add timing headers."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
