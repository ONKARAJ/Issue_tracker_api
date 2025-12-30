"""
Project model for Issue Tracker API.

This module defines the Project model for:
- Issue organization and grouping
- Project ownership and access control
- Project metadata
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from .base import BaseModel


class ProjectStatus(str, enum.Enum):
    """
    Project status enumeration.
    
    Status indicates project state.
    """
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(BaseModel):
    """
    Project model for organizing issues.
    
    Projects group related issues and define ownership.
    """
    
    __tablename__ = "projects"
    
    # Project fields
    name = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Project name (unique)"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Project description"
    )
    
    status = Column(
        String(50),
        nullable=False,
        default=ProjectStatus.PLANNING.value,
        comment="Project status"
    )
    
    # Ownership
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who owns the project"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Project creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )
    
    # Relationships
    owner = relationship("User")
    
    issues = relationship(
        "Issue",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    labels = relationship(
        "Label",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        """String representation of Project."""
        return f"<Project(id={self.id}, name='{self.name}')>"