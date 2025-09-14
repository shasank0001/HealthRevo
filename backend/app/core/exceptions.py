from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class AuthenticationError(HTTPException):
    """Authentication failed."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(HTTPException):
    """Insufficient permissions."""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ValidationError(HTTPException):
    """Data validation failed."""
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class NotFoundError(HTTPException):
    """Resource not found."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ConflictError(HTTPException):
    """Resource conflict."""
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class ProcessingError(HTTPException):
    """Processing failed."""
    def __init__(self, detail: str = "Processing failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


def setup_exception_handlers(app):
    """Setup global exception handlers for the FastAPI app."""
    
    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request, exc):
        resp = JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        # Preserve auth headers when present (e.g., WWW-Authenticate)
        if getattr(exc, "headers", None):
            for k, v in exc.headers.items():
                resp.headers[k] = v
        return resp
    
    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(request, exc):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    
    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request, exc):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    
    @app.exception_handler(ConflictError)
    async def conflict_exception_handler(request, exc):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    
    @app.exception_handler(ProcessingError)
    async def processing_exception_handler(request, exc):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
