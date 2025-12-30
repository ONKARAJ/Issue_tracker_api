"""
Comment service for Issue Tracker API.

This module provides business logic for:
- Comment CRUD operations
- Comment validation and moderation
- Issue comment relationships
- Comment threading
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict, Any
from uuid import UUID

from app.models.comment import Comment
from app.models.issue import Issue
from app.models.user import User, UserRole
from app.schemas.comment import CommentCreate
from app.schemas.common import PaginatedResponse
from .base_service import BaseService


class CommentService(BaseService[Comment]):
    """
    Service class for comment business logic.
    
    Provides comment management operations with:
    - Issue relationship validation
    - Author validation
    - Content validation
    - Soft delete functionality
    """
    
    def __init__(self, db: Session):
        """Initialize comment service."""
        super().__init__(db, Comment)
    
    def create_comment(self, comment_data: CommentCreate) -> Comment:
        """
        Create a new comment with validation.
        
        Args:
            comment_data: Comment creation data
            
        Returns:
            Created comment instance
            
        Raises:
            ValueError: If validation fails
        """
        # Verify issue exists and is not deleted
        issue = self.db.query(Issue).filter(
            and_(
                Issue.id == comment_data.issue_id,
                Issue.is_deleted == False
            )
        ).first()
        
        if not issue:
            raise ValueError("Issue not found")
        
        # Verify author exists and is active
        author = self.db.query(User).filter(
            and_(
                User.id == comment_data.author_id,
                User.is_deleted == False,
                User.is_active == True
            )
        ).first()
        
        if not author:
            raise ValueError("Author not found or inactive")
        
        # Validate content is non-empty
        if not comment_data.content or not comment_data.content.strip():
            raise ValueError("Comment content cannot be empty")
        
        # Create comment
        comment_dict = comment_data.dict()
        comment_dict['content'] = comment_dict['content'].strip()
        return self.create(comment_dict)
    
    def get_comment(self, comment_id: UUID) -> Optional[Comment]:
        """
        Get comment by ID.
        
        Args:
            comment_id: Comment UUID
            
        Returns:
            Comment instance or None
        """
        return self.get_by_id(str(comment_id))
    
    def delete_comment(self, comment_id: UUID) -> bool:
        """
        Soft delete comment.
        
        Args:
            comment_id: Comment UUID
            
        Returns:
            True if deleted, False if not found
        """
        return self.soft_delete(str(comment_id))
    
    def list_comments(self, issue_id: UUID, page: int = 1, size: int = 20) -> PaginatedResponse:
        """
        List comments for an issue with pagination.
        
        Args:
            issue_id: Issue UUID
            page: Page number
            size: Items per page
            
        Returns:
            Paginated list of comments
            
        Raises:
            ValueError: If issue not found
        """
        # Verify issue exists
        issue = self.db.query(Issue).filter(
            and_(
                Issue.id == issue_id,
                Issue.is_deleted == False
            )
        ).first()
        
        if not issue:
            raise ValueError("Issue not found")
        
        filters = {'issue_id': issue_id}
        return self.get_all(page=page, size=size, filters=filters, order_by='created_at', order_desc=False)
    
    def list_user_comments(self, user_id: UUID, page: int = 1, size: int = 20) -> PaginatedResponse:
        """
        List comments by a specific user.
        
        Args:
            user_id: User UUID
            page: Page number
            size: Items per page
            
        Returns:
            Paginated list of user's comments
        """
        filters = {'author_id': user_id}
        return self.get_all(page=page, size=size, filters=filters, order_by='created_at', order_desc=True)
    
    def update_comment(self, comment_id: UUID, content: str, user_id: UUID) -> Optional[Comment]:
        """
        Update comment content with authorization check.
        
        Args:
            comment_id: Comment UUID
            content: New comment content
            user_id: User UUID making the update
            
        Returns:
            Updated comment or None
            
        Raises:
            ValueError: If validation fails or unauthorized
        """
        comment = self.get_comment(comment_id)
        if not comment:
            return None
        
        # Check if user is the author
        if comment.author_id != user_id:
            raise ValueError("Only the comment author can update the comment")
        
        # Validate content
        if not content or not content.strip():
            raise ValueError("Comment content cannot be empty")
        
        return self.update(str(comment_id), {'content': content.strip()})
    
    def can_user_delete_comment(self, user: User, comment: Comment) -> bool:
        """
        Check if user can delete comment.
        
        Args:
            user: User instance
            comment: Comment instance
            
        Returns:
            True if user can delete comment
        """
        # Author can delete their own comments
        if comment.author_id == user.id:
            return True
        
        # Admin can delete any comment
        if user.has_permission(UserRole.ADMIN):
            return True
        
        # Issue creator or project owner can delete comments (if implemented)
        # This would require checking issue/project ownership
        
        return False
    
    def get_comment_statistics(self, issue_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Get comment statistics.
        
        Args:
            issue_id: Optional issue filter
            
        Returns:
            Dictionary with comment statistics
        """
        base_query = self.db.query(Comment).filter(Comment.is_deleted == False)
        
        if issue_id:
            base_query = base_query.filter(Comment.issue_id == issue_id)
        
        total_comments = base_query.count()
        
        return {
            'total_comments': total_comments,
        }
