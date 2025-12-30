"""
Common Pydantic schemas used across the API.

This module provides reusable schemas for:
- Pagination parameters and responses
- Error responses
- Common data structures
"""

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional
from datetime import datetime

T = TypeVar('T')


class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints.
    
    Attributes:
        page: Page number (1-indexed)
        size: Items per page
    """
    
    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-indexed)"
    )
    
    size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (max 100)"
    )


class PaginationMeta(BaseModel):
    """
    Pagination metadata for list responses.
    
    Attributes:
        page: Current page number
        size: Items per page
        total: Total number of items
        pages: Total number of pages
        has_next: Whether there's a next page
        has_prev: Whether there's a previous page
    """
    
    page: int = Field(description="Current page number")
    size: int = Field(description="Items per page")
    total: int = Field(description="Total number of items")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there's a next page")
    has_prev: bool = Field(description="Whether there's a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.
    
    Attributes:
        items: List of items for current page
        meta: Pagination metadata
    """
    
    model_config = {"arbitrary_types_allowed": True}
    
    items: List[T] = Field(description="List of items for current page")
    meta: PaginationMeta = Field(description="Pagination metadata")


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    
    Attributes:
        detail: Error description
        code: Optional error code for programmatic handling
        timestamp: Error timestamp
        path: Request path where error occurred
    """
    
    detail: str = Field(description="Error description")
    code: Optional[str] = Field(None, description="Optional error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    path: Optional[str] = Field(None, description="Request path where error occurred")


class HealthResponse(BaseModel):
    """
    Health check response.
    
    Attributes:
        status: Service health status
        service: Service name
        version: Service version
        timestamp: Check timestamp
    """
    
    status: str = Field(description="Service health status")
    service: str = Field(description="Service name")
    version: Optional[str] = Field(None, description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
