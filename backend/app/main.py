from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .api.endpoints import router as main_router
from .api.auth import router as auth_router
from .core.config import get_settings
from .utils.json_encoder import CustomJSONEncoder
from .core.errors import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from .core.rate_limiter import RateLimiter, ChatRateLimiter
from .core.monitoring import MetricsMiddleware, RequestLogger, metrics_collector
import json

settings = get_settings()

class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            cls=CustomJSONEncoder,
            ensure_ascii=False
        ).encode("utf-8")

app = FastAPI(
    title="Chatbot Builder API",
    default_response_class=CustomJSONResponse,
    description="Production-ready API for building and managing AI chatbots",
    version="1.0.0"
)

# ═══════════════════════════════════════════════════════════
#  ERROR HANDLERS
# ═══════════════════════════════════════════════════════════
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ═══════════════════════════════════════════════════════════
#  MIDDLEWARE (Order matters: first added = outermost layer)
# ═══════════════════════════════════════════════════════════

# 1. Request logging (outermost - logs everything)
app.add_middleware(RequestLogger)

# 2. Metrics collection
app.add_middleware(MetricsMiddleware)

# 3. Rate limiting
app.add_middleware(RateLimiter, requests_per_minute=60, requests_per_hour=1000)
app.add_middleware(ChatRateLimiter, requests_per_minute=20, requests_per_hour=200)

# 4. CORS (innermost - closest to routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════
#  METRICS ENDPOINT
# ═══════════════════════════════════════════════════════════

@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """
    Get application metrics
    Shows request counts, response times, error rates, etc.
    """
    return metrics_collector.get_metrics()

# ═══════════════════════════════════════════════════════════
#  ROUTERS
# ═══════════════════════════════════════════════════════════

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(main_router, prefix="/api", tags=["API"])
