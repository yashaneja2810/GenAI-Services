"""
Rate Limiting Middleware
Prevents API abuse by limiting requests per IP address
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import asyncio
import logging

logger = logging.getLogger(__name__)


class RateLimiter(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter
    For production, consider using Redis for distributed rate limiting
    """
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Storage: {ip: {minute: count, hour: count, minute_reset: datetime, hour_reset: datetime}}
        self.request_counts: Dict[str, Dict] = defaultdict(lambda: {
            "minute_count": 0,
            "hour_count": 0,
            "minute_reset": datetime.now(),
            "hour_reset": datetime.now()
        })
        
        # Cleanup task to prevent memory bloat
        asyncio.create_task(self._cleanup_old_entries())
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check
        if request.url.path == "/api/health":
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limits
        is_allowed, retry_after = self._check_rate_limit(client_ip)
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": 429,
                        "message": "Too many requests. Please slow down.",
                        "type": "RateLimitError",
                        "retry_after_seconds": retry_after
                    }
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            max(0, self.requests_per_minute - self.request_counts[client_ip]["minute_count"])
        )
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            max(0, self.requests_per_hour - self.request_counts[client_ip]["hour_count"])
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for proxy headers first
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> Tuple[bool, int]:
        """
        Check if client has exceeded rate limits
        Returns: (is_allowed, retry_after_seconds)
        """
        now = datetime.now()
        client_data = self.request_counts[client_ip]
        
        # Reset minute counter if needed
        if now >= client_data["minute_reset"]:
            client_data["minute_count"] = 0
            client_data["minute_reset"] = now + timedelta(minutes=1)
        
        # Reset hour counter if needed
        if now >= client_data["hour_reset"]:
            client_data["hour_count"] = 0
            client_data["hour_reset"] = now + timedelta(hours=1)
        
        # Check limits
        if client_data["minute_count"] >= self.requests_per_minute:
            retry_after = int((client_data["minute_reset"] - now).total_seconds())
            return False, max(retry_after, 1)
        
        if client_data["hour_count"] >= self.requests_per_hour:
            retry_after = int((client_data["hour_reset"] - now).total_seconds())
            return False, max(retry_after, 60)
        
        # Increment counters
        client_data["minute_count"] += 1
        client_data["hour_count"] += 1
        
        return True, 0
    
    async def _cleanup_old_entries(self):
        """Periodically remove old IP entries to prevent memory bloat"""
        while True:
            await asyncio.sleep(3600)  # Run every hour
            
            now = datetime.now()
            old_ips = []
            
            for ip, data in self.request_counts.items():
                # Remove if both counters are reset and no recent activity
                if (now >= data["minute_reset"] and 
                    now >= data["hour_reset"] and 
                    data["minute_count"] == 0 and 
                    data["hour_count"] == 0):
                    old_ips.append(ip)
            
            for ip in old_ips:
                del self.request_counts[ip]
            
            if old_ips:
                logger.info(f"Cleaned up {len(old_ips)} inactive IP entries from rate limiter")


class ChatRateLimiter(BaseHTTPMiddleware):
    """
    Special rate limiter for chat endpoints
    More restrictive to prevent bot abuse
    """
    
    def __init__(self, app, requests_per_minute: int = 20, requests_per_hour: int = 200):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.request_counts: Dict[str, Dict] = defaultdict(lambda: {
            "minute_count": 0,
            "hour_count": 0,
            "minute_reset": datetime.now(),
            "hour_reset": datetime.now()
        })
    
    async def dispatch(self, request: Request, call_next):
        # Only apply to chat endpoints
        if not (request.url.path.startswith("/api/chat") or "/chat" in request.url.path):
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        is_allowed, retry_after = self._check_rate_limit(client_ip)
        
        if not is_allowed:
            logger.warning(f"Chat rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": 429,
                        "message": "Too many chat requests. Please wait before trying again.",
                        "type": "ChatRateLimitError",
                        "retry_after_seconds": retry_after
                    }
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        response = await call_next(request)
        response.headers["X-Chat-RateLimit-Remaining"] = str(
            max(0, self.requests_per_minute - self.request_counts[client_ip]["minute_count"])
        )
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> Tuple[bool, int]:
        now = datetime.now()
        client_data = self.request_counts[client_ip]
        
        if now >= client_data["minute_reset"]:
            client_data["minute_count"] = 0
            client_data["minute_reset"] = now + timedelta(minutes=1)
        
        if now >= client_data["hour_reset"]:
            client_data["hour_count"] = 0
            client_data["hour_reset"] = now + timedelta(hours=1)
        
        if client_data["minute_count"] >= self.requests_per_minute:
            retry_after = int((client_data["minute_reset"] - now).total_seconds())
            return False, max(retry_after, 1)
        
        if client_data["hour_count"] >= self.requests_per_hour:
            retry_after = int((client_data["hour_reset"] - now).total_seconds())
            return False, max(retry_after, 60)
        
        client_data["minute_count"] += 1
        client_data["hour_count"] += 1
        
        return True, 0
