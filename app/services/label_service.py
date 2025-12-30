"""
Label service for Issue Tracker API.

This module provides business logic for:
- Label CRUD operations
- Label validation and uniqueness
- Project-specific labels
- Issue-label association management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict, Any, List
from uuid import UUID

from app.models.label import Label
from app.models.project import Project
from app.schemas.label import LabelCreate
from app.schemas.common import PaginatedResponse
from .base_service import BaseService


class LabelService(BaseService[Label]):
    """
    Service class for label business logic.
    
    Provides label management operations with:
    - Name uniqueness validation
    - Project association validation
    - Color validation
    - Soft delete functionality
    """
    
    def __init__(self, db: Session):
        """Initialize label service."""
        super().__init__(db, Label)
    
    def create_label(self, label_data: LabelCreate) -> Label:
        """
        Create a new label with validation.
        
        Args:
            label_data: Label creation data
            
        Returns:
            Created label instance
            
        Raises:
            ValueError: If validation fails
        """
        # Verify project exists if project_id is provided
        if label_data.project_id:
            project = self.db.query(Project).filter(
                and_(
                    Project.id == label_data.project_id,
                    Project.is_deleted == False
                )
            ).first()
            
            if not project:
                raise ValueError("Project not found")
        
        # Check if label name already exists
        existing_label = self.db.query(Label).filter(
            and_(
                Label.name == label_data.name,
                Label.is_deleted == False
            )
        ).first()
        
        if existing_label:
            raise ValueError(f"Label '{label_data.name}' already exists")
        
        # Create label
        label_dict = label_data.dict()
        return self.create(label_dict)
    
    def get_label(self, label_id: UUID) -> Optional[Label]:
        """
        Get label by ID.
        
        Args:
            label_id: Label UUID
            
        Returns:
            Label instance or None
        """
        return self.get_by_id(str(label_id))
    
    def update_label(self, label_id: UUID, label_data: Dict[str, Any]) -> Optional[Label]:
        """
        Update label with validation.
        
        Args:
            label_id: Label UUID
            label_data: Label update data
            
        Returns:
            Updated label or None
            
        Raises:
            ValueError: If validation fails
        """
        label = self.get_label(label_id)
        if not label:
            return None
        
        # Check name uniqueness if being updated
        if 'name' in label_data and label_data['name'] != label.name:
            existing_label = self.db.query(Label).filter(
                and_(
                    Label.name == label_data['name'],
                    Label.id != label_id,
                    Label.is_deleted == False
                )
            ).first()
            
            if existing_label:
                raise ValueError(f"Label '{label_data['name']}' already exists")
        
        # Verify project exists if project_id is being updated
        if 'project_id' in label_data and label_data['project_id']:
            project = self.db.query(Project).filter(
                and_(
                    Project.id == label_data['project_id'],
                    Project.is_deleted == False
                )
            ).first()
            
            if not project:
                raise ValueError("Project not found")
        
        return self.update(str(label_id), label_data)
    
    def delete_label(self, label_id: UUID) -> bool:
        """
        Soft delete label.
        
        Args:
            label_id: Label UUID
            
        Returns:
            True if deleted, False if not found
        """
        return self.soft_delete(str(label_id))
    
    def list_labels(self, page: int = 1, size: int = 20, project_id: Optional[UUID] = None) -> PaginatedResponse:
        """
        List labels with pagination and optional project filter.
        
        Args:
            page: Page number
            size: Items per page
            project_id: Optional project filter
            
        Returns:
            Paginated list of labels
        """
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        
        return self.get_all(page=page, size=size, filters=filters, order_by='name', order_desc=False)
    
    def get_global_labels(self, page: int = 1, size: int = 20) -> PaginatedResponse:
        """
        List global labels (not associated with any project).
        
        Args:
            page: Page number
            size: Items per page
            
        Returns:
            Paginated list of global labels
        """
        # Custom query for global labels
        query = self.db.query(Label).filter(
            and_(
                Label.is_deleted == False,
                Label.project_id.is_(None)
            )
        ).order_by(Label.name)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        from math import ceil
        offset = (page - 1) * size
        items = query.offset(offset).limit(size).all()
        
        # Calculate pagination metadata
        pages = ceil(total / size) if size > 0 else 0
        has_next = page < pages
        has_prev = page > 1
        
        from app.schemas.common import PaginationMeta
        meta = PaginationMeta(
            page=page,
            size=size,
            total=total,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return PaginatedResponse(items=items, meta=meta)
    
    def assign_label_to_issue(self, issue_id: UUID, label_id: UUID) -> bool:
        """
        Assign a label to an issue.
        
        Args:
            issue_id: Issue UUID
            label_id: Label UUID
            
        Returns:
            True if assigned successfully
            
        Raises:
            ValueError: If issue or label not found, or already assigned
        """
        from app.models.issue_label import IssueLabel
        
        # Verify issue exists
        issue = self.db.query(Issue).filter(
            and_(
                Issue.id == issue_id,
                Issue.is_deleted == False
            )
        ).first()
        
        if not issue:
            raise ValueError("Issue not found")
        
        # Verify label exists
        label = self.get_label(label_id)
        if not label:
            raise ValueError("Label not found")
        
        # Check if already assigned
        existing_assignment = self.db.query(IssueLabel).filter(
            and_(
                IssueLabel.issue_id == issue_id,
                IssueLabel.label_id == label_id
            )
        ).first()
        
        if existing_assignment:
            raise ValueError("Label already assigned to issue")
        
        # Create assignment
        assignment = IssueLabel(issue_id=issue_id, label_id=label_id)
        self.db.add(assignment)
        self.db.commit()
        
        return True
    
    def replace_issue_labels_atomically(self, issue_id: UUID, label_ids: List[UUID]) -> List[Label]:
        """
        Replace all labels for an issue atomically.
        
        Args:
            issue_id: Issue UUID
            label_ids: List of label UUIDs to assign
            
        Returns:
            List of assigned labels
            
        Raises:
            ValueError: If issue or labels not found
        """
        from app.models.issue_label import IssueLabel
        from app.database import DatabaseTransaction
        
        # Verify issue exists
        issue = self.db.query(Issue).filter(
            and_(
                Issue.id == issue_id,
                Issue.is_deleted == False
            )
        ).first()
        
        if not issue:
            raise ValueError("Issue not found")
        
        # Validate all labels exist
        if label_ids:
            labels = self.db.query(Label).filter(
                and_(
                    Label.id.in_(label_ids),
                    Label.is_deleted == False
                )
            ).all()
            
            if len(labels) != len(label_ids):
                found_ids = [label.id for label in labels]
                missing_ids = [lid for lid in label_ids if lid not in found_ids]
                raise ValueError(f"Labels not found: {missing_ids}")
        else:
            labels = []
        
        # Perform atomic operation in a single transaction
        with DatabaseTransaction(self.db) as db:
            # Remove existing labels
            db.query(IssueLabel).filter(IssueLabel.issue_id == issue_id).delete()
            
            # Add new labels
            for label_id in label_ids:
                assignment = IssueLabel(issue_id=issue_id, label_id=label_id)
                db.add(assignment)
        
        return labels
    
    def remove_label_from_issue(self, issue_id: UUID, label_id: UUID) -> bool:
        """
        Remove a label from an issue.
        
        Args:
            issue_id: Issue UUID
            label_id: Label UUID
            
        Returns:
            True if removed successfully
            
        Raises:
            ValueError: If assignment not found
        """
        from app.models.issue_label import IssueLabel
        
        assignment = self.db.query(IssueLabel).filter(
            and_(
                IssueLabel.issue_id == issue_id,
                IssueLabel.label_id == label_id
            )
        ).first()
        
        if not assignment:
            raise ValueError("Label not assigned to issue")
        
        self.db.delete(assignment)
        self.db.commit()
        
        return True
