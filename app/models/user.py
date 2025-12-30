"""
User model for Issue Tracker API.

This module defines the User model with:
- User authentication and authorization
- Role-based access control
- Profile information
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from .base import BaseModel


class UserRole(str, enum.Enum):
    """
    User role enumeration for role-based access control.
    
    Roles define permissions:
    - REPORTER: Can create and view issues
    - DEVELOPER: Can work on assigned issues
    - MANAGER: Can manage projects and users
    - ADMIN: Full system access
    """
    REPORTER = "reporter"
    DEVELOPER = "developer"
    MANAGER = "manager"
    ADMIN = "admin"


class User(BaseModel):
    """
    User model for authentication and authorization.
    
    Stores user account information, credentials, and profile data.
    """
    
    __tablename__ = "users"
    
    # Authentication fields
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email address (unique)"
    )
    
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hashed password using bcrypt"
    )
    
    # Profile fields
    full_name = Column(
        String(255),
        nullable=False,
        comment="User's full display name"
    )
    
    role = Column(
        String(50),
        nullable=False,
        default=UserRole.REPORTER.value,
        comment="User role for access control"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the user account is active"
    )
    
    # Optional profile fields
    avatar_url = Column(
        String(500),
        nullable=True,
        comment="URL to user's avatar image"
    )
    
    bio = Column(
        Text,
        nullable=True,
        comment="User biography or description"
    )
    
    # Timestamps
    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of last login"
    )
    
    # Relationships
    created_issues = relationship(
        "Issue",
        back_populates="creator",
        foreign_keys="Issue.creator_id"
    )
    
    assigned_issues = relationship(
        "Issue",
        back_populates="assignee",
        foreign_keys="Issue.assignee_id"
    )
    
    comments = relationship("Comment", back_populates="author")
    
    def __repr__(self):
        """String representation of User."""
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
