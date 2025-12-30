"""
Pydantic schemas for Attachment entity.

This module provides schemas for:
- Attachment responses
- File metadata validation
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID


class AttachmentBase(BaseModel):
    """
    Base attachment schema with common fields.
    """
    
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    content_type: str = Field(..., min_length=1, max_length=100, description="MIME type")


class AttachmentResponse(AttachmentBase):
    """
    Schema for attachment responses.
    
    Includes file path and metadata.
    """
    
    id: UUID = Field(description="Attachment's unique identifier")
    version: int = Field(description="Version for optimistic concurrency control")
    file_path: str = Field(description="Storage path for the file")
    issue_id: UUID = Field(description="ID of the issue")
    created_at: datetime = Field(description="Timestamp when attachment was created")
    updated_at: datetime = Field(description="Timestamp when attachment was last updated")
    is_deleted: bool = Field(description="Whether the attachment is soft-deleted")
    
    class Config:
        from_attributes = True


class AttachmentList(BaseModel):
    """
    Schema for attachment list responses.
    
    Used in paginated responses.
    """
    
    id: UUID = Field(description="Attachment's unique identifier")
    filename: str = Field(description="Original filename")
    file_size: int = Field(description="File size in bytes")
    content_type: str = Field(description="MIME type")
    issue_id: UUID = Field(description="ID of the issue")
    created_at: datetime = Field(description="Timestamp when attachment was created")
    
    class Config:
        from_attributes = True
