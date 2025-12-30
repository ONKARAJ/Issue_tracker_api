"""
Comment router for Issue Tracker API.

This module provides REST endpoints for:
- Comment CRUD operations
- Comment threading and replies
- Comment moderation
- Issue comment integration

Follows REST conventions with proper HTTP status codes,
error handling, and request validation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentList,
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.services.comment_service import CommentService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CommentList])
async def list_comments(
    pagination: PaginationParams = Depends(),
    issue_id: UUID = Query(..., description="Filter by issue ID"),
    db: Session = Depends(get_db),
):
    """
    List comments for an issue with pagination.
    
    Args:
        pagination: Pagination parameters
        issue_id: Issue UUID to filter comments
        db: Database session
        
    Returns:
        Paginated list of comments
    """
    service = CommentService(db)
    return service.list_comments(
        page=pagination.page,
        size=pagination.size,
        issue_id=issue_id,
    )


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a single comment by ID.
    
    Args:
        comment_id: Comment UUID
        db: Database session
        
    Returns:
        Comment details
        
    Raises:
        HTTPException: If comment not found
    """
    service = CommentService(db)
    comment = service.get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.post("/", response_model=CommentResponse, status_code=201)
async def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new comment.
    
    Args:
        comment_data: Comment creation data
        db: Database session
        
    Returns:
        Created comment
        
    Raises:
        HTTPException: If validation fails
    """
    service = CommentService(db)
    try:
        return service.create_comment(comment_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Soft delete a comment.
    
    Args:
        comment_id: Comment UUID
        db: Database session
        
    Raises:
        HTTPException: If comment not found
    """
    service = CommentService(db)
    success = service.delete_comment(comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
