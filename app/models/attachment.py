"""
Attachment model for Issue Tracker API.

This module defines the Attachment model for:
- File uploads associated with issues
- File metadata storage
- Secure file management
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class Attachment(BaseModel):
    """
    Attachment model for file uploads on issues.
    
    Stores metadata about uploaded files.
    """
    
    __tablename__ = "attachments"
    
    # File metadata
    filename = Column(
        String(255),
        nullable=False,
        comment="Original filename"
    )
    
    file_path = Column(
        String(500),
        nullable=False,
        comment="Server path to stored file"
    )
    
    content_type = Column(
        String(100),
        nullable=False,
        comment="MIME type of the file"
    )
    
    file_size = Column(
        Integer,
        nullable=False,
        comment="File size in bytes"
    )
    
    # Relationships
    issue_id = Column(
        UUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Issue this attachment belongs to"
    )
    
    uploader_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who uploaded the file"
    )
    
    # Timestamps
    uploaded_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Upload timestamp"
    )
    
    # Relationships
    issue = relationship("Issue", back_populates="attachments")
    uploader = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('ix_attachments_issue_uploaded', 'issue_id', 'uploaded_at'),
        Index('ix_attachments_uploader_uploaded', 'uploader_id', 'uploaded_at'),
    )
    
    def __repr__(self):
        """String representation of Attachment."""
        return f"<Attachment(id={self.id}, filename='{self.filename}', issue_id={self.issue_id})>"