"""
Simplified Issue router for Issue Tracker API.

This module provides REST endpoints for:
- Issue CRUD operations using direct SQL queries

Follows REST conventions with proper HTTP status codes,
error handling, and request validation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import logging

from app.database import get_db
from app.schemas.common import PaginationParams, PaginatedResponse

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_issues(
    pagination: PaginationParams = Depends(),
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assignee_id: Optional[UUID] = Query(None, description="Filter by assignee ID"),
    db: Session = Depends(get_db),
):
    """
    List issues with pagination and filtering using direct SQL queries.
    
    Args:
        pagination: Pagination parameters
        project_id: Optional project filter
        status: Optional status filter
        assignee_id: Optional assignee filter
        db: Database session
        
    Returns:
        Paginated list of issues
    """
    logger.info(f"Listing issues with page={pagination.page}, size={pagination.size}, project_id={project_id}, status={status}, assignee_id={assignee_id}")
    
    try:
        # Build base query with filters
        query = "SELECT * FROM issues WHERE is_deleted = false"
        params = {}
        
        # Apply filters
        if project_id:
            query += " AND project_id = :project_id"
            params["project_id"] = str(project_id)
        
        if status:
            query += " AND status = :status"
            params["status"] = status
        
        if assignee_id:
            query += " AND assignee_id = :assignee_id"
            params["assignee_id"] = str(assignee_id)
        
        # Order by created_at descending for most recent first
        query += " ORDER BY created_at DESC"
        
        # Get total count
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        from sqlalchemy import text
        count_result = db.execute(text(count_query), params)
        total = count_result.fetchone()[0]
        logger.info(f"Total count: {total}")
        
        # Apply pagination
        offset = (pagination.page - 1) * pagination.size
        limit = pagination.size
        
        # Add pagination to query
        paginated_query = query + " LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        # Execute query
        result = db.execute(text(paginated_query), params)
        issues = result.fetchall()
        logger.info(f"Retrieved {len(issues)} issues")
        
        # Convert to dict for response
        issue_dicts = []
        for issue in issues:
            issue_dict = {
                "id": str(issue[0]),  # id
                "title": issue[1],    # title
                "type": issue[2],     # type
                "status": issue[3],   # status
                "priority": issue[4], # priority
                "project_id": str(issue[5]) if issue[5] else None,  # project_id
                "assignee_id": str(issue[6]) if issue[6] else None,  # assignee_id
                "created_at": issue[7].isoformat() if issue[7] else None,  # created_at
            }
            issue_dicts.append(issue_dict)
        
        # Calculate pagination metadata
        from math import ceil
        pages = ceil(total / pagination.size) if pagination.size > 0 else 0
        has_next = pagination.page < pages
        has_prev = pagination.page > 1
        
        from app.schemas.common import PaginationMeta
        meta = PaginationMeta(
            page=pagination.page,
            size=pagination.size,
            total=total,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        logger.info(f"Returning paginated response with {len(issue_dicts)} items")
        return PaginatedResponse(items=issue_dicts, meta=meta)
        
    except Exception as e:
        logger.error(f"Error in list_issues: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{issue_id}")
async def get_issue(
    issue_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a single issue by ID using direct SQL query.
    
    Args:
        issue_id: Issue UUID
        db: Database session
        
    Returns:
        Issue details
        
    Raises:
        HTTPException: If issue not found
    """
    logger.info(f"Getting issue with ID: {issue_id}")
    
    try:
        from sqlalchemy import text
        query = text("SELECT * FROM issues WHERE id = :id AND is_deleted = false")
        result = db.execute(query, {"id": str(issue_id)})
        issue = result.fetchone()
        
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        # Convert to dict for response
        issue_dict = {
            "id": str(issue[0]),  # id
            "title": issue[1],    # title
            "description": issue[2],  # description
            "type": issue[3],     # type
            "status": issue[4],   # status
            "priority": issue[5], # priority
            "project_id": str(issue[6]) if issue[6] else None,  # project_id
            "creator_id": str(issue[7]) if issue[7] else None,  # creator_id
            "assignee_id": str(issue[8]) if issue[8] else None,  # assignee_id
            "created_at": issue[9].isoformat() if issue[9] else None,  # created_at
            "updated_at": issue[10].isoformat() if issue[10] else None,  # updated_at
            "resolved_at": issue[11].isoformat() if issue[11] else None,  # resolved_at
            "closed_at": issue[12].isoformat() if issue[12] else None,  # closed_at
            "version": issue[13],  # version
            "is_deleted": issue[14],  # is_deleted
        }
        
        logger.info(f"Returning issue: {issue_dict['title']}")
        return issue_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_issue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
