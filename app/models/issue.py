"""
Issue model for Issue Tracker API.

This module defines the Issue model with:
- Issue tracking with workflow states
- Priority and type classification
- Assignment and ownership
- Timestamps and metadata
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from .base import BaseModel


class IssueStatus(str, enum.Enum):
    """
    Issue status enumeration for workflow management.
    
    Status progression: OPEN -> IN_PROGRESS -> RESOLVED -> CLOSED
    """
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IssueType(str, enum.Enum):
    """
    Issue type enumeration for categorization.
    
    Types help classify the nature of the issue.
    """
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    TASK = "task"
    EPIC = "epic"


class IssuePriority(str, enum.Enum):
    """
    Issue priority enumeration for urgency classification.
    
    Priorities help determine processing order.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Issue(BaseModel):
    """
    Issue model for tracking bugs, features, and tasks.
    
    Core entity with workflow, assignment, and metadata.
    """
    
    __tablename__ = "issues"
    
    # Core issue fields
    title = Column(
        String(500),
        nullable=False,
        comment="Issue title/summary"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed issue description"
    )
    
    # Classification
    status = Column(
        String(50),
        nullable=False,
        default=IssueStatus.OPEN.value,
        comment="Current issue status"
    )
    
    type = Column(
        String(50),
        nullable=False,
        default=IssueType.TASK.value,
        comment="Issue type/category"
    )
    
    priority = Column(
        String(50),
        nullable=False,
        default=IssuePriority.MEDIUM.value,
        comment="Issue priority level"
    )
    
    # Relationships
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Project this issue belongs to"
    )
    
    creator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who created the issue"
    )
    
    assignee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User assigned to work on the issue"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Issue creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )
    
    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when issue was resolved"
    )
    
    closed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when issue was closed"
    )
    
    # Temporarily comment out ALL relationships to isolate user creation issues
    # project = relationship(
    #     "Project",
    #     back_populates="issues"
    # )
    # 
    # creator = relationship(
    #     "User",
    #     back_populates="created_issues",
    #     foreign_keys=[creator_id]
    # )
    # 
    # assignee = relationship(
    #     "User",
    #     back_populates="assigned_issues",
    #     foreign_keys=[assignee_id]
    # )
    # 
    # comments = relationship(
    #     "Comment",
    #     back_populates="issue",
    #     cascade="all, delete-orphan"
    # )
    # 
    # labels = relationship(
    #     "Label",
    #     secondary="issue_labels",
    #     back_populates="issues"
    # )
    # 
    # attachments = relationship(
    #     "Attachment",
    #     back_populates="issue",
    #     cascade="all, delete-orphan"
    # )
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_issues_project_status', 'project_id', 'status'),
        Index('ix_issues_assignee_status', 'assignee_id', 'status'),
        Index('ix_issues_creator_created', 'creator_id', 'created_at'),
    )
    
    def __repr__(self):
        """String representation of Issue."""
        return f"<Issue(id={self.id}, title='{self.title}', status='{self.status}')>"
