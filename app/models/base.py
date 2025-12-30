"""
Base model with common fields for all SQLAlchemy models.

This module provides a base class that includes:
- Primary key with UUID generation
- Version field for optimistic concurrency control
- Created and updated timestamps
- Soft delete functionality
"""

from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common fields.
    
    All models should inherit from this to ensure:
    - Consistent primary key structure
    - Optimistic concurrency control
    - Audit timestamps
    - Soft delete capability
    """
    
    __abstract__ = True
    
    # Primary key using UUID for distributed systems compatibility
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="Unique identifier for the record"
    )
    
    # Version field for optimistic concurrency control
    # Incremented on each update to prevent lost updates
    version = Column(
        Integer,
        default=1,
        nullable=False,
        comment="Version for optimistic concurrency control"
    )
    
    # Audit timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Timestamp when record was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Timestamp when record was last updated"
    )
    
    # Soft delete flag
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Flag for soft delete (true if record is deleted)"
    )
    
    def increment_version(self):
        """Increment version for optimistic concurrency control."""
        self.version += 1
        
    def soft_delete(self):
        """Mark record as deleted without removing from database."""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
        
    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.updated_at = datetime.utcnow()
