"""
Centralized Error Handling Module
Provides custom exceptions and error handlers for the application
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from typing import Union

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  CUSTOM EXCEPTIONS
# ═══════════════════════════════════════════════════════════

class BotNotFoundError(HTTPException):
    """Raised when a bot is not found"""
    def __init__(self, bot_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with ID '{bot_id}' not found"
        )


class BotAccessDeniedError(HTTPException):
    """Raised when user doesn't have access to a bot"""
    def __init__(self, bot_id: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to bot '{bot_id}'"
        )


class DocumentProcessingError(HTTPException):
    """Raised when document processing fails"""
    def __init__(self, filename: str, reason: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process document '{filename}': {reason}"
        )


class VectorStoreError(HTTPException):
    """Raised when vector store operations fail"""
    def __init__(self, operation: str, reason: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Vector store {operation} failed: {reason}"
        )


class AIServiceError(HTTPException):
    """Raised when AI service (Groq) fails"""
    def __init__(self, reason: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {reason}"
        )


class WebScraperError(HTTPException):
    """Raised when web scraping fails"""
    def __init__(self, url: str, reason: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to scrape '{url}': {reason}"
        )


class AuthenticationError(HTTPException):
    """Raised when authentication fails"""
    def __init__(self, reason: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=reason,
            headers={"WWW-Authenticate": "Bearer"}
        )


class RateLimitError(HTTPException):
    """Raised when rate limit is exceeded"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(retry_after)}
        )


# ═══════════════════════════════════════════════════════════
#  ERROR HANDLERS
# ═══════════════════════════════════════════════════════════

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format"""
    logger.error(
        f"HTTP Exception: {exc.status_code} - {exc.detail} | "
        f"Path: {request.url.path} | Method: {request.method}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": exc.__class__.__name__
            }
        },
        headers=exc.headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed information"""
    logger.error(f"Validation Error: {exc.errors()} | Path: {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "Validation error",
                "type": "ValidationError",
                "details": exc.errors()
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully"""
    logger.error(
        f"Unexpected Error: {str(exc)} | Path: {request.url.path}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "An unexpected error occurred. Please try again later.",
                "type": "InternalServerError"
            }
        }
    )


# ═══════════════════════════════════════════════════════════
#  ERROR RESPONSE HELPERS
# ═══════════════════════════════════════════════════════════

def create_error_response(
    status_code: int,
    message: str,
    error_type: str = "Error",
    details: Union[dict, list, None] = None
) -> JSONResponse:
    """Create a standardized error response"""
    content = {
        "error": {
            "code": status_code,
            "message": message,
            "type": error_type
        }
    }
    
    if details:
        content["error"]["details"] = details
    
    return JSONResponse(status_code=status_code, content=content)
