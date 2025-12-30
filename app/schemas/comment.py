"""
Pydantic schemas for Comment entity.

This module provides schemas for:
- Comment creation
- Comment responses with relationships
- Input validation and serialization
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID


class CommentBase(BaseModel):
    """
    Base comment schema with common fields.
    """
    
    content: str = Field(..., min_length=1, max_length=2000, description="Comment content")


class CommentCreate(CommentBase):
    """
    Schema for comment creation requests.
    
    Attributes:
        author_id: ID of the comment author
        issue_id: ID of the issue this comment belongs to
    """
    
    author_id: UUID = Field(description="ID of the user writing this comment")
    issue_id: UUID = Field(description="ID of the issue this comment belongs to")
    
    @validator('content')
    def validate_content(cls, v):
        """Validate comment content."""
        if not v or not v.strip():
            raise ValueError('Comment content cannot be empty')
        return v.strip()


class CommentResponse(CommentBase):
    """
    Schema for comment responses.
    
    Includes author information and metadata.
    """
    
    id: UUID = Field(description="Comment's unique identifier")
    version: int = Field(description="Version for optimistic concurrency control")
    author_id: UUID = Field(description="ID of the comment author")
    issue_id: UUID = Field(description="ID of the issue")
    created_at: datetime = Field(description="Timestamp when comment was created")
    updated_at: datetime = Field(description="Timestamp when comment was last updated")
    is_deleted: bool = Field(description="Whether the comment is soft-deleted")
    
    class Config:
        from_attributes = True


class CommentList(BaseModel):
    """
    Schema for comment list responses.
    
    Used in paginated responses.
    """
    
    id: UUID = Field(description="Comment's unique identifier")
    content: str = Field(description="Comment content")
    author_id: UUID = Field(description="ID of the comment author")
    issue_id: UUID = Field(description="ID of the issue")
    created_at: datetime = Field(description="Timestamp when comment was created")
    
    class Config:
        from_attributes = True
