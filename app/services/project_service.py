"""
Project service for Issue Tracker API.

This module provides business logic for:
- Project CRUD operations
- Project ownership and permissions
- Project status management
- Project statistics and metrics
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict, Any
from uuid import UUID

from app.models.project import Project, ProjectStatus
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.common import PaginatedResponse
from .base_service import BaseService


class ProjectService(BaseService[Project]):
    """
    Service class for project business logic.
    
    Provides project management operations with:
    - Ownership validation
    - Status management
    - Permission checking
    - Soft delete functionality
    """
    
    def __init__(self, db: Session):
        """Initialize project service."""
        super().__init__(db, Project)
    
    def create_project(self, project_data: ProjectCreate) -> Project:
        """
        Create a new project with ownership validation.
        
        Args:
            project_data: Project creation data
            
        Returns:
            Created project instance
            
        Raises:
            ValueError: If owner not found or validation fails
        """
        # Verify owner exists and is active
        owner = self.db.query(User).filter(
            and_(
                User.id == project_data.owner_id,
                User.is_deleted == False,
                User.is_active == True
            )
        ).first()
        
        if not owner:
            raise ValueError("Owner not found or inactive")
        
        # Check if project name already exists for this owner
        existing_project = self.db.query(Project).filter(
            and_(
                Project.name == project_data.name,
                Project.owner_id == project_data.owner_id,
                Project.is_deleted == False
            )
        ).first()
        
        if existing_project:
            raise ValueError(f"Project '{project_data.name}' already exists for this owner")
        
        # Create project
        project_dict = project_data.dict()
        return self.create(project_dict)
    
    def get_project(self, project_id: UUID) -> Optional[Project]:
        """
        Get project by ID.
        
        Args:
            project_id: Project UUID
            
        Returns:
            Project instance or None
        """
        return self.get_by_id(str(project_id))
    
    def update_project(self, project_id: UUID, project_data: ProjectUpdate) -> Optional[Project]:
        """
        Update project with validation.
        
        Args:
            project_id: Project UUID
            project_data: Project update data
            
        Returns:
            Updated project or None
            
        Raises:
            ValueError: If validation fails
        """
        # Check name uniqueness if being updated
        project = self.get_project(project_id)
        if not project:
            return None
        
        if project_data.name and project_data.name != project.name:
            existing_project = self.db.query(Project).filter(
                and_(
                    Project.name == project_data.name,
                    Project.owner_id == project.owner_id,
                    Project.id != project_id,
                    Project.is_deleted == False
                )
            ).first()
            
            if existing_project:
                raise ValueError(f"Project '{project_data.name}' already exists for this owner")
        
        # Prepare update data
        update_dict = project_data.dict(exclude_unset=True)
        return self.update(str(project_id), update_dict)
    
    def partial_update_project(self, project_id: UUID, project_data: ProjectUpdate) -> Optional[Project]:
        """
        Partially update project.
        
        Args:
            project_id: Project UUID
            project_data: Partial project update data
            
        Returns:
            Updated project or None
        """
        return self.update_project(project_id, project_data)
    
    def delete_project(self, project_id: UUID) -> bool:
        """
        Soft delete project.
        
        Args:
            project_id: Project UUID
            
        Returns:
            True if deleted, False if not found
        """
        return self.soft_delete(str(project_id))
    
    def list_projects(self, page: int = 1, size: int = 20) -> PaginatedResponse:
        """
        List projects with pagination.
        
        Args:
            page: Page number
            size: Items per page
            
        Returns:
            Paginated list of projects
        """
        return self.get_all(page=page, size=size, order_by='created_at', order_desc=True)
    
    def list_user_projects(self, user_id: UUID, page: int = 1, size: int = 20) -> PaginatedResponse:
        """
        List projects owned by a specific user.
        
        Args:
            user_id: User UUID
            page: Page number
            size: Items per page
            
        Returns:
            Paginated list of user's projects
        """
        filters = {'owner_id': user_id}
        return self.get_all(page=page, size=size, filters=filters, order_by='created_at', order_desc=True)
    
    def can_user_access_project(self, user: User, project: Project) -> bool:
        """
        Check if user can access project.
        
        Args:
            user: User instance
            project: Project instance
            
        Returns:
            True if user can access project
        """
        # Owner can always access
        if project.owner_id == user.id:
            return True
        
        # Admin can access all projects
        if user.has_permission(UserRole.ADMIN):
            return True
        
        # Manager can access projects they're assigned to (if implemented)
        # This would require project assignments table
        
        return False
    
    def can_user_modify_project(self, user: User, project: Project) -> bool:
        """
        Check if user can modify project.
        
        Args:
            user: User instance
            project: Project instance
            
        Returns:
            True if user can modify project
        """
        # Owner can always modify
        if project.owner_id == user.id:
            return True
        
        # Admin can modify all projects
        if user.has_permission(UserRole.ADMIN):
            return True
        
        return False
    
    def get_project_statistics(self, project_id: UUID) -> Dict[str, Any]:
        """
        Get project statistics.
        
        Args:
            project_id: Project UUID
            
        Returns:
            Dictionary with project statistics
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError("Project not found")
        
        # This would be implemented with actual queries
        # For now, return placeholder data
        return {
            'total_issues': 0,
            'open_issues': 0,
            'closed_issues': 0,
            'total_comments': 0,
            'total_attachments': 0,
        }
