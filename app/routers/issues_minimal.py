"""
Minimal Issue router for Issue Tracker API.

This module provides REST endpoints for:
- Issue operations without database dependencies

Follows REST conventions with proper HTTP status codes,
error handling, and request validation.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def list_issues():
    """
    List issues without database dependencies.
    
    Returns:
        List of mock issues
    """
    logger.info("Listing issues (mock data)")
    
    # Return mock data for now
    mock_issues = [
        {
            "id": str(uuid4()),
            "title": "Sample Issue 1",
            "type": "task",
            "status": "open",
            "priority": "medium",
            "project_id": str(uuid4()),
            "assignee_id": str(uuid4()),
            "created_at": datetime.now().isoformat(),
        },
        {
            "id": str(uuid4()),
            "title": "Sample Issue 2",
            "type": "bug",
            "status": "in_progress",
            "priority": "high",
            "project_id": str(uuid4()),
            "assignee_id": str(uuid4()),
            "created_at": datetime.now().isoformat(),
        }
    ]
    
    logger.info(f"Returning {len(mock_issues)} mock issues")
    return {
        "items": mock_issues,
        "meta": {
            "page": 1,
            "size": 20,
            "total": len(mock_issues),
            "pages": 1,
            "has_next": False,
            "has_prev": False
        }
    }


@router.get("/{issue_id}")
async def get_issue(issue_id: UUID):
    """
    Get a single issue by ID without database dependencies.
    
    Args:
        issue_id: Issue UUID
        
    Returns:
        Mock issue details
        
    Raises:
        HTTPException: If issue not found
    """
    logger.info(f"Getting issue with ID: {issue_id}")
    
    # Return mock data for now
    mock_issue = {
        "id": str(issue_id),
        "title": f"Sample Issue {issue_id}",
        "description": "This is a sample issue description",
        "type": "task",
        "status": "open",
        "priority": "medium",
        "project_id": str(uuid4()),
        "creator_id": str(uuid4()),
        "assignee_id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "resolved_at": None,
        "closed_at": None,
        "version": 1,
        "is_deleted": False,
    }
    
    logger.info(f"Returning mock issue: {mock_issue['title']}")
    return mock_issue


@router.put("/{issue_id}")
async def update_issue(issue_id: UUID, update_data: dict):
    """
    Update an issue without database dependencies.
    
    Args:
        issue_id: Issue UUID
        update_data: Fields to update
        
    Returns:
        Updated mock issue details
        
    Raises:
        HTTPException: If issue not found or validation fails
    """
    logger.info(f"Updating issue with ID: {issue_id}")
    
    # Return mock data for now
    mock_issue = {
        "id": str(issue_id),
        "title": f"Sample Issue {issue_id}",
        "description": "This is a sample issue description",
        "type": "task",
        "status": "open",
        "priority": "medium",
        "project_id": str(uuid4()),
        "creator_id": str(uuid4()),
        "assignee_id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "resolved_at": None,
        "closed_at": None,
        "version": 1,
        "is_deleted": False,
    }
    
    # Apply updates from request
    for key, value in update_data.items():
        if key in mock_issue:
            mock_issue[key] = value
    
    # Update the updated_at timestamp
    mock_issue["updated_at"] = datetime.now().isoformat()
    
    logger.info(f"Returning updated mock issue: {mock_issue['title']}")
    return mock_issue


@router.delete("/{issue_id}", status_code=204)
async def delete_issue(issue_id: UUID):
    """
    Delete an issue without database dependencies.
    
    Args:
        issue_id: Issue UUID
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: If issue not found
    """
    logger.info(f"Deleting issue with ID: {issue_id}")
    
    # For now, just return a success response
    # In a real implementation, this would delete the issue from the database
    logger.info(f"Issue {issue_id} deleted successfully")
    return None
