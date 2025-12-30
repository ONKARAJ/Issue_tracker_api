"""
Pydantic schemas for label assignment operations.

This module provides schemas for:
- Bulk label assignment operations
- Label validation and management
"""

from pydantic import BaseModel, Field
from typing import List
from uuid import UUID


class LabelAssignmentRequest(BaseModel):
    """
    Schema for label assignment requests.
    
    Attributes:
        label_ids: List of label UUIDs to assign to issue
    """
    
    label_ids: List[UUID] = Field(..., min_items=0, description="List of label IDs to assign")


class LabelAssignmentResponse(BaseModel):
    """
    Schema for label assignment responses.
    
    Attributes:
        assigned_labels: List of assigned labels
        message: Success message
    """
    
    assigned_labels: List[UUID] = Field(description="List of assigned label IDs")
    message: str = Field(description="Operation result message")
