"""
Monitoring and Metrics Module
Tracks application performance and usage metrics
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from collections import defaultdict
from typing import Dict
import time
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Simple in-memory metrics collector"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.endpoint_stats: Dict[str, Dict] = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "errors": 0
        })
        self.status_codes: Dict[int, int] = defaultdict(int)
        self.start_time = datetime.now()
    
    def record_request(self, path: str, method: str, status_code: int, response_time: float):
        """Record a completed request"""
        self.request_count += 1
        
        # Track by endpoint
        endpoint_key = f"{method} {path}"
        self.endpoint_stats[endpoint_key]["count"] += 1
        self.endpoint_stats[endpoint_key]["total_time"] += response_time
        
        # Track errors
        if status_code >= 400:
            self.error_count += 1
            self.endpoint_stats[endpoint_key]["errors"] += 1
        
        # Track status codes
        self.status_codes[status_code] += 1
    
    def get_metrics(self) -> dict:
        """Get current metrics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate average response times
        endpoint_metrics = {}
        for endpoint, stats in self.endpoint_stats.items():
            avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
            endpoint_metrics[endpoint] = {
                "requests": stats["count"],
                "avg_response_time_ms": round(avg_time * 1000, 2),
                "errors": stats["errors"],
                "error_rate": round(stats["errors"] / stats["count"] * 100, 2) if stats["count"] > 0 else 0
            }
        
        return {
            "uptime_seconds": round(uptime, 2),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": round(self.error_count / self.request_count * 100, 2) if self.request_count > 0 else 0,
            "requests_per_second": round(self.request_count / uptime, 2) if uptime > 0 else 0,
            "status_codes": dict(self.status_codes),
            "endpoints": endpoint_metrics
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.request_count = 0
        self.error_count = 0
        self.endpoint_stats.clear()
        self.status_codes.clear()
        self.start_time = datetime.now()


# Global metrics collector instance
metrics_collector = MetricsCollector()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics"""
    
    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Record metrics
        metrics_collector.record_request(
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            response_time=response_time
        )
        
        # Add response time header
        response.headers["X-Response-Time"] = f"{round(response_time * 1000, 2)}ms"
        
        return response


class RequestLogger(BaseHTTPMiddleware):
    """Middleware to log all requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Log incoming request
        logger.info(f"→ {request.method} {request.url.path} | Client: {request.client.host if request.client else 'unknown'}")
        
        start_time = time.time()
        response = await call_next(request)
        response_time = time.time() - start_time
        
        # Log response
        log_method = logger.info if response.status_code < 400 else logger.error
        log_method(
            f"← {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {round(response_time * 1000, 2)}ms"
        )
        
        return response
