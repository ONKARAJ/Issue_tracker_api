"""
Base service class for Issue Tracker API.

This module provides a foundation for all service classes with:
- Common database operations
- Pagination utilities
- Error handling patterns
- Optimistic concurrency control
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from math import ceil

from app.models.base import BaseModel
from app.schemas.common import PaginationParams, PaginatedResponse, PaginationMeta

T = TypeVar('T', bound=BaseModel)


class BaseService(ABC, Generic[T]):
    """
    Abstract base service class providing common functionality.
    
    All service classes should inherit from this to ensure:
    - Consistent pagination handling
    - Standard error handling
    - Optimistic concurrency control
    - Common CRUD patterns
    """
    
    def __init__(self, db: Session, model_class: type[T]):
        """
        Initialize service with database session and model class.
        
        Args:
            db: SQLAlchemy database session
            model_class: SQLAlchemy model class
        """
        self.db = db
        self.model_class = model_class
    
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Get entity by ID with soft delete filtering.
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            Entity instance or None if not found
        """
        return self.db.query(self.model_class).filter(
            and_(
                self.model_class.id == entity_id,
                self.model_class.is_deleted == False
            )
        ).first()
    
    def get_all(
        self,
        page: int = 1,
        size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> PaginatedResponse[List[T]]:
        """
        Get paginated list of entities with filtering and sorting.
        
        Args:
            page: Page number (1-indexed)
            size: Items per page
            filters: Dictionary of field filters
            order_by: Field to sort by
            order_desc: Sort direction (True for descending)
            
        Returns:
            Paginated response with entities
        """
        # Build base query
        query = self.db.query(self.model_class).filter(
            self.model_class.is_deleted == False
        )
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    query = query.filter(getattr(self.model_class, field) == value)
        
        # Apply ordering
        if order_by and hasattr(self.model_class, order_by):
            order_field = getattr(self.model_class, order_by)
            query = query.order_by(desc(order_field) if order_desc else asc(order_field))
        else:
            # Default ordering by created_at descending
            query = query.order_by(desc(self.model_class.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        items = query.offset(offset).limit(size).all()
        
        # Calculate pagination metadata
        pages = ceil(total / size) if size > 0 else 0
        has_next = page < pages
        has_prev = page > 1
        
        meta = PaginationMeta(
            page=page,
            size=size,
            total=total,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return PaginatedResponse(items=items, meta=meta)
    
    def create(self, entity_data: Dict[str, Any]) -> T:
        """
        Create new entity.
        
        Args:
            entity_data: Dictionary of entity data
            
        Returns:
            Created entity instance
        """
        entity = self.model_class(**entity_data)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Update entity with optimistic concurrency control.
        
        Args:
            entity_id: Entity UUID
            update_data: Dictionary of update data
            
        Returns:
            Updated entity or None if not found
            
        Raises:
            ValueError: If version mismatch (concurrency conflict)
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            return None
        
        # Check version for optimistic concurrency control
        expected_version = update_data.get('version')
        if expected_version is not None and entity.version != expected_version:
            raise ValueError(f"Version conflict: expected {expected_version}, got {entity.version}")
        
        # Update fields
        for field, value in update_data.items():
            if field != 'version' and hasattr(entity, field):
                setattr(entity, field, value)
        
        # Increment version
        entity.increment_version()
        
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def soft_delete(self, entity_id: str) -> bool:
        """
        Soft delete entity.
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            True if deleted, False if not found
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            return False
        
        entity.soft_delete()
        self.db.commit()
        return True
    
    def restore(self, entity_id: str) -> bool:
        """
        Restore soft-deleted entity.
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            True if restored, False if not found
        """
        entity = self.db.query(self.model_class).filter(
            and_(
                self.model_class.id == entity_id,
                self.model_class.is_deleted == True
            )
        ).first()
        
        if not entity:
            return False
        
        entity.restore()
        self.db.commit()
        return True
