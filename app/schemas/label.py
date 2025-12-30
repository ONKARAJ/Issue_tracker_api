"""
Pydantic schemas for Label entity.

This module provides schemas for:
- Label creation and responses
- Input validation and serialization
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class LabelBase(BaseModel):
    """
    Base label schema with common fields.
    """
    
    name: str = Field(..., min_length=1, max_length=100, description="Label name")
    color: Optional[str] = Field("#007bff", pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")
    description: Optional[str] = Field(None, max_length=255, description="Label description")
    project_id: Optional[UUID] = Field(None, description="Optional project ID for project-specific labels")


class LabelCreate(LabelBase):
    """
    Schema for label creation requests.
    """
    
    @validator('name')
    def validate_name(cls, v):
        """Validate label name."""
        if not v or not v.strip():
            raise ValueError('Label name cannot be empty')
        return v.strip()


class LabelResponse(LabelBase):
    """
    Schema for label responses.
    
    Includes metadata and relationships.
    """
    
    id: UUID = Field(description="Label's unique identifier")
    version: int = Field(description="Version for optimistic concurrency control")
    created_at: datetime = Field(description="Timestamp when label was created")
    updated_at: datetime = Field(description="Timestamp when label was last updated")
    is_deleted: bool = Field(description="Whether the label is soft-deleted")
    
    class Config:
        from_attributes = True


class LabelList(BaseModel):
    """
    Schema for label list responses.
    
    Used in paginated responses.
    """
    
    id: UUID = Field(description="Label's unique identifier")
    name: str = Field(description="Label name")
    color: str = Field(description="Hex color code")
    project_id: Optional[UUID] = Field(None, description="Project ID if project-specific")
    created_at: datetime = Field(description="Timestamp when label was created")
    
    class Config:
        from_attributes = True
