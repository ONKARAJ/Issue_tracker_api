"""
Project router for Issue Tracker API.

This module provides REST endpoints for:
- Project CRUD operations
- Project status management
- Project ownership and permissions
- Project statistics and metrics

Follows REST conventions with proper HTTP status codes,
error handling, and request validation.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectList,
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[ProjectList])
async def list_projects(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    """
    List projects with pagination.
    
    Args:
        pagination: Pagination parameters
        db: Database session
        
    Returns:
        Paginated list of projects
    """
    service = ProjectService(db)
    return service.list_projects(page=pagination.page, size=pagination.size)


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new project.
    
    Args:
        project_data: Project creation data
        db: Database session
        
    Returns:
        Created project
        
    Raises:
        HTTPException: If validation fails
    """
    service = ProjectService(db)
    try:
        return service.create_project(project_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an entire project.
    
    Args:
        project_id: Project UUID
        project_data: Project update data
        db: Database session
        
    Returns:
        Updated project
        
    Raises:
        HTTPException: If project not found or validation fails
    """
    service = ProjectService(db)
    try:
        project = service.update_project(project_id, project_data)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Soft delete a project.
    
    Args:
        project_id: Project UUID
        db: Database session
        
    Raises:
        HTTPException: If project not found
    """
    service = ProjectService(db)
    success = service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
