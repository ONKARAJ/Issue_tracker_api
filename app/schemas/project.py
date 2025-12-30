"""
Pydantic schemas for Project entity.

This module provides schemas for:
- Project creation and updates
- Project responses with relationships
- Input validation and serialization
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    """
    Base project schema with common fields.
    """
    
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    status: ProjectStatus = Field(default=ProjectStatus.PLANNING, description="Project status")


class ProjectCreate(ProjectBase):
    """
    Schema for project creation requests.
    
    Attributes:
        owner_id: ID of the project owner
    """
    
    owner_id: UUID = Field(description="ID of the user who will own this project")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate project name."""
        if not v or not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip()


class ProjectUpdate(BaseModel):
    """
    Schema for project update requests.
    
    All fields are optional to allow partial updates.
    """
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    status: Optional[ProjectStatus] = Field(None, description="Project status")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate project name if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Project name cannot be empty')
            return v.strip()
        return v


class ProjectResponse(ProjectBase):
    """
    Schema for project responses.
    
    Includes owner information and metadata.
    """
    
    id: UUID = Field(description="Project's unique identifier")
    version: int = Field(description="Version for optimistic concurrency control")
    owner_id: UUID = Field(description="ID of the project owner")
    created_at: datetime = Field(description="Timestamp when project was created")
    updated_at: datetime = Field(description="Timestamp when project was last updated")
    is_deleted: bool = Field(description="Whether the project is soft-deleted")
    
    class Config:
        from_attributes = True


class ProjectList(BaseModel):
    """
    Schema for project list responses.
    
    Used in paginated responses.
    """
    
    id: UUID = Field(description="Project's unique identifier")
    name: str = Field(description="Project name")
    status: ProjectStatus = Field(description="Project status")
    owner_id: UUID = Field(description="ID of the project owner")
    created_at: datetime = Field(description="Timestamp when project was created")
    
    class Config:
        from_attributes = True
