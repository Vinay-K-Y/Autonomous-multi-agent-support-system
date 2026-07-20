from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings

# Create limiter instance with in-memory storage
# Note: slowapi doesn't have built-in Redis storage in the current version
# For distributed rate limiting, consider using a different library or custom implementation
limiter = Limiter(key_func=get_remote_address)
print("Rate limiting: Using in-memory storage")


def setup_rate_limiting(app):
    """
    Setup rate limiting for the FastAPI application.
    Call this in main.py after creating the app.
    """
    if settings.RATE_LIMIT_ENABLED:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        return True
    return False


# Rate limit decorators for common use cases
def rate_limit_requests(requests: int = settings.RATE_LIMIT_REQUESTS, period: int = settings.RATE_LIMIT_PERIOD):
    """
    Rate limit decorator for endpoints.
    Usage:
    
    @router.get("/api/v1/support")
    @rate_limit_requests(requests=100, period=60)
    async def support_endpoint(request: Request):
        ...
    """
    def decorator(func):
        return limiter.limit(f"{requests}/{period}")(func)
    return decorator


# Custom rate limit by user ID (for authenticated users)
def rate_limit_by_user(requests: int = 200, period: int = 60):
    """
    Rate limit by user ID for authenticated users.
    This allows higher limits for authenticated users.
    """
    def get_user_id(request: Request) -> str:
        # Try to get user from request state (set by auth middleware)
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.id}"
        # Fallback to IP address
        return get_remote_address(request)
    
    def decorator(func):
        return limiter.limit(f"{requests}/{period}", key_func=get_user_id)(func)
    return decorator
