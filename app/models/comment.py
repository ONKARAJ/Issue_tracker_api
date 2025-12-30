"""
Comment model for Issue Tracker API.

This module defines the Comment model for:
- Issue discussions and conversations
- Author tracking
- Timestamps
"""

from sqlalchemy import Column, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class Comment(BaseModel):
    """
    Comment model for issue discussions.
    
    Allows users to add comments to issues for collaboration.
    """
    
    __tablename__ = "comments"
    
    # Comment content
    content = Column(
        Text,
        nullable=False,
        comment="Comment text content"
    )
    
    # Relationships
    issue_id = Column(
        UUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Issue this comment belongs to"
    )
    
    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who wrote the comment"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Comment creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )
    
    # Relationships
    issue = relationship("Issue", back_populates="comments")
    author = relationship("User", back_populates="comments")
    
    # Indexes
    __table_args__ = (
        Index('ix_comments_issue_created', 'issue_id', 'created_at'),
        Index('ix_comments_author_created', 'author_id', 'created_at'),
    )
    
    def __repr__(self):
        """String representation of Comment."""
        return f"<Comment(id={self.id}, issue_id={self.issue_id}, author_id={self.author_id})>"
