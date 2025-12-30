"""
Attachment service for Issue Tracker API.

This module provides business logic for:
- Attachment metadata management
"""

import os
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.attachment import Attachment
from app.models.issue import Issue
from app.schemas.common import PaginatedResponse
from .base_service import BaseService


class AttachmentService(BaseService[Attachment]):
    """
    Service class for attachment business logic.
    
    Provides attachment management operations with:
    - Metadata management
    - Access control
    """
    
    def __init__(self, db: Session):
        """
        Initialize attachment service.
        
        Args:
            db: Database session
        """
        super().__init__(db, Attachment)
    
    def get_attachment(self, attachment_id: str) -> Optional[Attachment]:
        """
        Get attachment by ID.
        
        Args:
            attachment_id: Attachment UUID
            
        Returns:
            Attachment instance or None
        """
        return self.get_by_id(attachment_id)
    
    def delete_attachment(self, attachment_id: str) -> bool:
        """
        Delete attachment (soft delete).
        
        Args:
            attachment_id: Attachment UUID
            
        Returns:
            True if deleted, False if not found
        """
        attachment = self.get_attachment(attachment_id)
        if not attachment:
            return False
        
        # Soft delete the record
        success = self.soft_delete(attachment_id)
        
        return success
    
    def list_attachments(self, issue_id: str, page: int = 1, size: int = 20) -> PaginatedResponse:
        """
        List attachments for an issue with pagination.
        
        Args:
            issue_id: Issue UUID
            page: Page number
            size: Items per page
            
        Returns:
            Paginated list of attachments
            
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
        return self.get_all(page=page, size=size, filters=filters, order_by='created_at', order_desc=True)
