"""
Reports router for Issue Tracker API.

This module provides REST endpoints for:
- Top assignees reporting
- Issue latency metrics
- Performance analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/top-assignees")
async def get_top_assignees(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of assignees to return"),
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db),
):
    """
    Get assignees ordered by number of assigned issues.
    
    Args:
        limit: Maximum number of assignees to return
        project_id: Optional project filter
        db: Database session
        
    Returns:
        List of assignees with issue counts
    """
    service = ReportService(db)
    try:
        return service.get_top_assignees(limit=limit, project_id=project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/latency")
async def get_resolution_latency(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db),
):
    """
    Get average resolution time for resolved issues.
    
    Args:
        days: Number of days to look back
        project_id: Optional project filter
        db: Database session
        
    Returns:
        Resolution latency statistics
    """
    service = ReportService(db)
    try:
        return service.get_resolution_latency(days=days, project_id=project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/velocity")
async def get_issue_velocity(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db),
):
    """
    Get issue creation and resolution velocity.
    
    Args:
        days: Number of days to look back
        project_id: Optional project filter
        db: Database session
        
    Returns:
        Issue velocity metrics
    """
    service = ReportService(db)
    try:
        return service.get_issue_velocity(days=days, project_id=project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
