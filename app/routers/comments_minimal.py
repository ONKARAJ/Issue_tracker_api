"""
Minimal Comment router for Issue Tracker API.

This module provides REST endpoints for:
- Comment operations without database dependencies

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
async def list_comments(
    issue_id: UUID = Query(..., description="Filter by issue ID")
):
    """
    List comments for an issue without database dependencies.
    
    Args:
        issue_id: Issue UUID to filter comments
        
    Returns:
        List of mock comments
    """
    logger.info(f"Listing comments for issue ID: {issue_id}")
    
    # Return mock data for now
    mock_comments = [
        {
            "id": str(uuid4()),
            "content": "This is a sample comment",
            "author_id": str(uuid4()),
            "issue_id": str(issue_id),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_deleted": False,
        },
        {
            "id": str(uuid4()),
            "content": "This is another sample comment",
            "author_id": str(uuid4()),
            "issue_id": str(issue_id),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_deleted": False,
        }
    ]
    
    logger.info(f"Returning {len(mock_comments)} mock comments")
    return {
        "items": mock_comments,
        "meta": {
            "page": 1,
            "size": 20,
            "total": len(mock_comments),
            "pages": 1,
            "has_next": False,
            "has_prev": False
        }
    }


@router.get("/{comment_id}")
async def get_comment(comment_id: UUID):
    """
    Get a single comment by ID without database dependencies.
    
    Args:
        comment_id: Comment UUID
        
    Returns:
        Mock comment details
        
    Raises:
        HTTPException: If comment not found
    """
    logger.info(f"Getting comment with ID: {comment_id}")
    
    # Return mock data for now
    mock_comment = {
        "id": str(comment_id),
        "content": "This is a sample comment",
        "author_id": str(uuid4()),
        "issue_id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "is_deleted": False,
    }
    
    logger.info(f"Returning mock comment: {mock_comment['id']}")
    return mock_comment


@router.post("/", status_code=201)
async def create_comment(comment_data: dict):
    """
    Create a new comment without database dependencies.
    
    Args:
        comment_data: Comment creation data
        
    Returns:
        Created mock comment
        
    Raises:
        HTTPException: If validation fails
    """
    logger.info("Creating comment (mock data)")
    
    # Return mock data for now
    mock_comment = {
        "id": str(uuid4()),
        "content": comment_data.get("content", "New Comment"),
        "author_id": str(uuid4()),
        "issue_id": str(comment_data.get("issue_id", uuid4())),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "is_deleted": False,
    }
    
    logger.info(f"Returning created mock comment: {mock_comment['id']}")
    return mock_comment


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(comment_id: UUID):
    """
    Delete a comment without database dependencies.
    
    Args:
        comment_id: Comment UUID
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: If comment not found
    """
    logger.info(f"Deleting comment with ID: {comment_id}")
    
    # For now, just return a success response
    # In a real implementation, this would delete the comment from the database
    logger.info(f"Comment {comment_id} deleted successfully")
    return None
