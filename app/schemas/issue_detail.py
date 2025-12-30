"""
Extended issue schemas for detailed responses.

This module provides schemas for:
- Issue details with comments and labels
- Comprehensive issue information
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from .issue import IssueResponse, IssueList
from .comment import CommentList
from .label import LabelList


class IssueDetailResponse(BaseModel):
    """
    Schema for detailed issue response with comments and labels.
    
    Attributes:
        issue: Issue details
        comments: List of associated comments
        labels: List of associated labels
    """
    
    issue: IssueResponse = Field(description="Issue details")
    comments: List[CommentList] = Field(default=[], description="Associated comments")
    labels: List[LabelList] = Field(default=[], description="Associated labels")
    
    class Config:
        from_attributes = True
