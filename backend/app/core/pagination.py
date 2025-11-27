"""Pagination utilities."""
from typing import TypeVar, Generic, List
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar('T')


class Page(BaseModel, Generic[T]):
    """Paginated response."""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
    
    class Config:
        arbitrary_types_allowed = True


def paginate(query: Query, page: int = 1, per_page: int = 10) -> Page:
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Items per page
        
    Returns:
        Page object with items and metadata
    """
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10
    if per_page > 100:
        per_page = 100
    
    total = query.count()
    pages = (total + per_page - 1) // per_page
    
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()
    
    return Page(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )
