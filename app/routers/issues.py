"""
Issue router for Issue Tracker API.

This module provides REST endpoints for:
- Issue CRUD operations

Follows REST conventions with proper HTTP status codes,
error handling, and request validation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.schemas.issue import (
    IssueUpdate,
    IssueResponse,
    IssueList,
)
from app.schemas.issue_detail import IssueDetailResponse
from app.schemas.common import PaginationParams, PaginatedResponse
from app.services.issue_service import IssueService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[IssueList])
async def list_issues(
    pagination: PaginationParams = Depends(),
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assignee_id: Optional[UUID] = Query(None, description="Filter by assignee ID"),
    db: Session = Depends(get_db),
):
    """
    List issues with pagination and filtering.
    
    Args:
        pagination: Pagination parameters
        project_id: Optional project filter
        status: Optional status filter
        assignee_id: Optional assignee filter
        db: Database session
        
    Returns:
        Paginated list of issues
    """
    service = IssueService(db)
    return service.list_issues(
        page=pagination.page,
        size=pagination.size,
        project_id=project_id,
        status=status,
        assignee_id=assignee_id,
    )


@router.get("/{issue_id}", response_model=IssueDetailResponse)
async def get_issue(
    issue_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a single issue by ID with comments and labels.
    
    Args:
        issue_id: Issue UUID
        db: Database session
        
    Returns:
        Issue details with comments and labels
        
    Raises:
        HTTPException: If issue not found
    """
    service = IssueService(db)
    result = service.get_issue_with_details(issue_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    return IssueDetailResponse(
        issue=result['issue'],
        comments=result['comments'],
        labels=result['labels']
    )


@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: UUID,
    issue_data: IssueUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an entire issue.
    
    Args:
        issue_id: Issue UUID
        issue_data: Issue update data
        db: Database session
        
    Returns:
        Updated issue
        
    Raises:
        HTTPException: If issue not found or validation fails
    """
    service = IssueService(db)
    try:
        issue = service.update_issue(issue_id, issue_data)
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        return issue
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{issue_id}", status_code=204)
async def delete_issue(
    issue_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Soft delete an issue.
    
    Args:
        issue_id: Issue UUID
        db: Database session
        
    Raises:
        HTTPException: If issue not found
    """
    service = IssueService(db)
    success = service.delete_issue(issue_id)
    if not success:
        raise HTTPException(status_code=404, detail="Issue not found")