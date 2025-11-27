"""Rate limiting middleware for API endpoints."""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limit."""
        async with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(minutes=1)
            
            # Remove old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > cutoff
            ]
            
            # Check limit
            if len(self.requests[identifier]) >= self.requests_per_minute:
                return False
            
            # Add current request
            self.requests[identifier].append(now)
            return True
    
    async def cleanup(self):
        """Periodic cleanup of old entries."""
        while True:
            await asyncio.sleep(60)  # Cleanup every minute
            async with self.lock:
                now = datetime.utcnow()
                cutoff = now - timedelta(minutes=5)
                
                # Remove entries older than 5 minutes
                to_remove = []
                for identifier, timestamps in self.requests.items():
                    self.requests[identifier] = [
                        ts for ts in timestamps if ts > cutoff
                    ]
                    if not self.requests[identifier]:
                        to_remove.append(identifier)
                
                for identifier in to_remove:
                    del self.requests[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    # Get client identifier (IP address or API key)
    client_ip = request.client.host if request.client else "unknown"
    
    # Skip rate limiting for health check
    if request.url.path == "/health":
        return await call_next(request)
    
    # Check rate limit
    if not await rate_limiter.check_rate_limit(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later."
            }
        )
    
    response = await call_next(request)
    return response
