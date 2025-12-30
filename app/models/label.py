"""
Label model for Issue Tracker API.

This module defines the Label model for:
- Issue categorization and tagging
- Color coding for visual organization
- Project-specific or global labels
"""

from sqlalchemy import Column, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel


class Label(BaseModel):
    """
    Label model for categorizing and tagging issues.
    
    Labels help organize issues with colors and names.
    Can be project-specific or global.
    """
    
    __tablename__ = "labels"
    
    # Label fields
    name = Column(
        String(100),
        nullable=False,
        comment="Label name"
    )
    
    color = Column(
        String(7),
        nullable=False,
        default="#007bff",
        comment="Hex color code for the label"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Optional description of the label"
    )
    
    # Optional project association
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Project this label belongs to (null for global labels)"
    )
    
    # Relationships
    project = relationship("Project", back_populates="labels")
    
    issues = relationship(
        "Issue",
        secondary="issue_labels",
        back_populates="labels"
    )
    
    # Indexes
    __table_args__ = (
        Index('ix_labels_project_name', 'project_id', 'name'),
        Index('ix_labels_name_global', 'name'),
    )
    
    def __repr__(self):
        """String representation of Label."""
        return f"<Label(id={self.id}, name='{self.name}', color='{self.color}')>"
