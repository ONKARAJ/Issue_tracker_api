"""
Pydantic schemas for Issue entity.

This module provides schemas for:
- Issue creation and updates
- Issue responses with relationships
- Input validation and serialization
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.issue import IssueType, IssueStatus, IssuePriority


class IssueBase(BaseModel):
    """
    Base issue schema with common fields.
    """
    
    title: str = Field(..., min_length=1, max_length=255, description="Issue title")
    description: Optional[str] = Field(None, max_length=5000, description="Issue description")
    type: IssueType = Field(default=IssueType.TASK, description="Issue type")
    priority: IssuePriority = Field(default=IssuePriority.MEDIUM, description="Issue priority")


class IssueCreate(IssueBase):
    """
    Schema for issue creation requests.
    
    Attributes:
        project_id: ID of the project
        creator_id: ID of the issue creator
        assignee_id: Optional ID of the assigned user
    """
    
    project_id: UUID = Field(description="ID of the project this issue belongs to")
    creator_id: UUID = Field(description="ID of the user creating this issue")
    assignee_id: Optional[UUID] = Field(None, description="ID of the user assigned to this issue")
    
    @validator('title')
    def validate_title(cls, v):
        """Validate issue title."""
        if not v or not v.strip():
            raise ValueError('Issue title cannot be empty')
        return v.strip()


class IssueUpdate(BaseModel):
    """
    Schema for issue update requests.
    
    All fields are optional to allow partial updates.
    """
    
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Issue title")
    description: Optional[str] = Field(None, max_length=5000, description="Issue description")
    type: Optional[IssueType] = Field(None, description="Issue type")
    status: Optional[IssueStatus] = Field(None, description="Issue status")
    priority: Optional[IssuePriority] = Field(None, description="Issue priority")
    assignee_id: Optional[UUID] = Field(None, description="ID of the user assigned to this issue")
    version: int = Field(..., description="Version for optimistic concurrency control")
    
    @validator('title')
    def validate_title(cls, v):
        """Validate issue title if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Issue title cannot be empty')
            return v.strip()
        return v


class IssueStatusUpdate(BaseModel):
    """
    Schema for issue status updates only.
    
    Used for workflow transitions.
    """
    
    status: IssueStatus = Field(description="New issue status")
    
    @validator('status')
    def validate_status_transition(cls, v, values):
        """Validate status transition (requires current status)."""
        # This would be implemented in the service layer with access to current status
        return v


class IssueResponse(IssueBase):
    """
    Schema for issue responses.
    
    Includes all relationships and metadata.
    """
    
    id: UUID = Field(description="Issue's unique identifier")
    version: int = Field(description="Version for optimistic concurrency control")
    status: IssueStatus = Field(description="Current issue status")
    project_id: UUID = Field(description="ID of the project")
    creator_id: Optional[UUID] = Field(None, description="ID of the creator")
    assignee_id: Optional[UUID] = Field(None, description="ID of the assignee")
    created_at: datetime = Field(description="Timestamp when issue was created")
    updated_at: datetime = Field(description="Timestamp when issue was last updated")
    is_deleted: bool = Field(description="Whether the issue is soft-deleted")
    
    class Config:
        from_attributes = True


class IssueList(BaseModel):
    """
    Schema for issue list responses.
    
    Used in paginated responses.
    """
    
    id: UUID = Field(description="Issue's unique identifier")
    title: str = Field(description="Issue title")
    type: IssueType = Field(description="Issue type")
    status: IssueStatus = Field(description="Current issue status")
    priority: IssuePriority = Field(description="Issue priority")
    project_id: UUID = Field(description="ID of the project")
    assignee_id: Optional[UUID] = Field(None, description="ID of the assignee")
    created_at: datetime = Field(description="Timestamp when issue was created")
    
    class Config:
        from_attributes = True
