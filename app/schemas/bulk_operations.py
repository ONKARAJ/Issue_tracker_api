"""
Pydantic schemas for bulk operations.

This module provides schemas for:
- Bulk status updates
- Bulk operation results
- Error reporting for bulk operations
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.issue import IssueStatus


class BulkStatusUpdateRequest(BaseModel):
    """
    Schema for bulk status update requests.
    
    Attributes:
        issue_ids: List of issue UUIDs to update
        new_status: New status to apply to all issues
    """
    
    issue_ids: List[UUID] = Field(..., min_items=1, description="List of issue IDs to update")
    new_status: IssueStatus = Field(..., description="New status to apply")


class BulkOperationError(BaseModel):
    """
    Schema for individual operation errors.
    
    Attributes:
        issue_id: Issue UUID that failed
        error: Error message
    """
    
    issue_id: UUID = Field(description="Issue ID that failed")
    error: str = Field(description="Error message")


class BulkStatusUpdateResponse(BaseModel):
    """
    Schema for bulk status update responses.
    
    Attributes:
        success_count: Number of successfully updated issues
        failure_count: Number of failed updates
        errors: List of errors for failed operations
        message: Summary message
    """
    
    success_count: int = Field(description="Number of successfully updated issues")
    failure_count: int = Field(description="Number of failed updates")
    errors: List[BulkOperationError] = Field(default=[], description="Errors for failed operations")
    message: str = Field(description="Operation summary message")
