"""
Issue-Label association model for Issue Tracker API.

This module defines the many-to-many relationship between issues and labels.
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class IssueLabel(BaseModel):
    """
    Association model for issue-label relationships.
    
    Represents the many-to-many relationship between issues and labels.
    """
    
    __tablename__ = "issue_labels"
    
    issue_id = Column(
        UUID(as_uuid=True),
        ForeignKey('issues.id', ondelete='CASCADE'),
        nullable=False,
        comment="Issue ID"
    )
    
    label_id = Column(
        UUID(as_uuid=True),
        ForeignKey('labels.id', ondelete='CASCADE'),
        nullable=False,
        comment="Label ID"
    )