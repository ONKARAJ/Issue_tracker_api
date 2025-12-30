"""
Attachment router for Issue Tracker API.

This module provides REST endpoints for:
- Attachment metadata management
- Issue attachment integration

Follows REST conventions with proper HTTP status codes,
error handling, and request validation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.attachment import (
    AttachmentResponse,
    AttachmentList,
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.services.attachment_service import AttachmentService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[AttachmentList])
async def list_attachments(
    pagination: PaginationParams = Depends(),
    issue_id: UUID = Query(..., description="Filter by issue ID"),
    db: Session = Depends(get_db),
):
    """
    List attachments for an issue with pagination.
    
    Args:
        pagination: Pagination parameters
        issue_id: Issue UUID to filter attachments
        db: Database session
        
    Returns:
        Paginated list of attachments
    """
    service = AttachmentService(db)
    return service.list_attachments(
        page=pagination.page,
        size=pagination.size,
        issue_id=issue_id,
    )


@router.get("/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get attachment metadata by ID.
    
    Args:
        attachment_id: Attachment UUID
        db: Database session
        
    Returns:
        Attachment metadata
        
    Raises:
        HTTPException: If attachment not found
    """
    service = AttachmentService(db)
    attachment = service.get_attachment(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return attachment


@router.delete("/{attachment_id}", status_code=204)
async def delete_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete an attachment (soft delete).
    
    Args:
        attachment_id: Attachment UUID
        db: Database session
        
    Raises:
        HTTPException: If attachment not found
    """
    service = AttachmentService(db)
    success = service.delete_attachment(attachment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Attachment not found")
