import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from app.config import settings
from app.observability.logging import logger


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class RateLimiter:
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}

    def get_bucket_key(self, request: Request) -> str:
        api_key = request.headers.get(settings.api_key_header, "")
        client_ip = request.client.host if request.client else "unknown"
        return f"{api_key}:{client_ip}"

    async def check_rate_limit(self, request: Request):
        key = self.get_bucket_key(request)
        if key not in self.buckets:
            self.buckets[key] = TokenBucket(
                capacity=settings.rate_limit_requests,
                refill_rate=settings.rate_limit_requests / settings.rate_limit_window_seconds,
            )

        if not self.buckets[key].consume():
            logger.warning("Rate limit exceeded", extra={"key": key})
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after_seconds": settings.rate_limit_window_seconds,
                }
            )


rate_limiter = RateLimiter()
