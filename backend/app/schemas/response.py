"""API response schemas."""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """Standard success response."""

    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    per_page: int
    total: int
    pages: int


class PaginatedResponse(BaseModel):
    """Paginated response."""

    items: list
    meta: PaginationMeta
