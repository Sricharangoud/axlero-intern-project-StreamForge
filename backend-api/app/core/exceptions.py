from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class StreamForgeException(Exception):
    """Base custom exception for StreamForge domain errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundException(StreamForgeException):
    """Raised when a requested database entity or resource is not found."""
    pass


class DuplicateEntityException(StreamForgeException):
    """Raised when attempting to create an entity that already exists (e.g. duplicate email)."""
    pass


class InvalidCredentialsException(StreamForgeException):
    """Raised when authentication fails due to invalid username or password."""
    pass


class UnauthorizedException(StreamForgeException):
    """Raised when a user attempts an action without proper authorization or permissions."""
    pass


class KafkaStreamException(StreamForgeException):
    """Raised when an error occurs during Kafka event producing or consuming."""
    pass


# Global FastAPI Exception Handlers
async def streamforge_exception_handler(request: Request, exc: StreamForgeException) -> JSONResponse:
    """
    Translates custom StreamForge domain exceptions into structured HTTP JSON responses.
    """
    logger.warning(f"Domain exception occurred on {request.method} {request.url.path}: {exc.message}")
    
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(exc, EntityNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DuplicateEntityException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, InvalidCredentialsException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, UnauthorizedException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, KafkaStreamException):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details
        }
    )


async def global_unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catches unexpected uncaught internal server errors to prevent revealing internal stack traces to clients.
    """
    logger.error(f"Unhandled internal server error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "InternalServerError",
            "message": "An unexpected error occurred on the server. Please contact support.",
            "details": {}
        }
    )
