"""
Minimal Attachment router for Issue Tracker API.

This module provides REST endpoints for:
- Attachment operations without database dependencies

Follows REST conventions with proper HTTP status codes,
error handling, and request validation.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def list_attachments(
    issue_id: Optional[UUID] = Query(None, description="Filter by issue ID")
):
    """
    List attachments for an issue without database dependencies.
    
    Args:
        issue_id: Issue UUID to filter attachments (optional)
        
    Returns:
        List of mock attachments
    """
    # Use provided issue_id or generate a random one for mock data
    filter_issue_id = str(issue_id) if issue_id else str(uuid4())
    logger.info(f"Listing attachments for issue ID: {filter_issue_id}")
    
    # Return mock data for now
    mock_attachments = [
        {
            "id": str(uuid4()),
            "filename": "sample_file.txt",
            "content_type": "text/plain",
            "size": 1024,
            "issue_id": filter_issue_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_deleted": False,
        },
        {
            "id": str(uuid4()),
            "filename": "another_file.pdf",
            "content_type": "application/pdf",
            "size": 2048,
            "issue_id": filter_issue_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_deleted": False,
        }
    ]
    
    logger.info(f"Returning {len(mock_attachments)} mock attachments")
    return {
        "items": mock_attachments,
        "meta": {
            "page": 1,
            "size": 20,
            "total": len(mock_attachments),
            "pages": 1,
            "has_next": False,
            "has_prev": False
        }
    }


@router.get("/{attachment_id}")
async def get_attachment(attachment_id: UUID):
    """
    Get a single attachment by ID without database dependencies.
    
    Args:
        attachment_id: Attachment UUID
        
    Returns:
        Mock attachment details
        
    Raises:
        HTTPException: If attachment not found
    """
    logger.info(f"Getting attachment with ID: {attachment_id}")
    
    # Return mock data for now
    mock_attachment = {
        "id": str(attachment_id),
        "filename": "sample_file.txt",
        "content_type": "text/plain",
        "size": 1024,
        "issue_id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "is_deleted": False,
    }
    
    logger.info(f"Returning mock attachment: {mock_attachment['filename']}")
    return mock_attachment


@router.delete("/{attachment_id}", status_code=204)
async def delete_attachment(attachment_id: UUID):
    """
    Delete an attachment without database dependencies.
    
    Args:
        attachment_id: Attachment UUID
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: If attachment not found
    """
    logger.info(f"Deleting attachment with ID: {attachment_id}")
    
    # For now, just return a success response
    # In a real implementation, this would delete the attachment from the database
    logger.info(f"Attachment {attachment_id} deleted successfully")
    return None
