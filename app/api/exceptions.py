from typing import Any, Optional, Dict

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class APIError(HTTPException):
    """Base API Exception"""

    def __init__(
        self, status_code: int, detail: str, headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class InternalError(APIError):
    """Database related errors"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {detail}",
        )


class NotFoundError(APIError):
    """Resource not found errors"""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with identifier {identifier} not found",
        )


class InvalidParameterError(APIError):
    """Invalid parameter errors"""

    def __init__(self, parameter: str, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter '{parameter}': {detail}",
        )


# Define your exception handlers here as before
async def api_error_handler(request, exc: APIError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def general_error_handler(request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )
