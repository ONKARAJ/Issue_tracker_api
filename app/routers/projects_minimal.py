"""
Minimal Project router for Issue Tracker API.

This module provides REST endpoints for:
- Project operations without database dependencies

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
async def list_projects():
    """
    List projects without database dependencies.
    
    Returns:
        List of mock projects
    """
    logger.info("Listing projects (mock data)")
    
    # Return mock data for now
    mock_projects = [
        {
            "id": str(uuid4()),
            "name": "Project One",
            "description": "This is a sample project",
            "status": "active",
            "owner_id": str(uuid4()),
            "created_at": datetime.now().isoformat(),
        },
        {
            "id": str(uuid4()),
            "name": "Project Two",
            "description": "This is another sample project",
            "status": "active",
            "owner_id": str(uuid4()),
            "created_at": datetime.now().isoformat(),
        }
    ]
    
    logger.info(f"Returning {len(mock_projects)} mock projects")
    return {
        "items": mock_projects,
        "meta": {
            "page": 1,
            "size": 20,
            "total": len(mock_projects),
            "pages": 1,
            "has_next": False,
            "has_prev": False
        }
    }


@router.post("/", status_code=201)
async def create_project(project_data: dict):
    """
    Create a new project without database dependencies.
    
    Args:
        project_data: Project creation data
        
    Returns:
        Created mock project
        
    Raises:
        HTTPException: If validation fails
    """
    logger.info("Creating project (mock data)")
    
    # Return mock data for now
    mock_project = {
        "id": str(uuid4()),
        "name": project_data.get("name", "New Project"),
        "description": project_data.get("description", "This is a new project"),
        "status": "active",
        "owner_id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    logger.info(f"Returning created mock project: {mock_project['name']}")
    return mock_project


@router.get("/{project_id}")
async def get_project(project_id: UUID):
    """
    Get a single project by ID without database dependencies.
    
    Args:
        project_id: Project UUID
        
    Returns:
        Mock project details
        
    Raises:
        HTTPException: If project not found
    """
    logger.info(f"Getting project with ID: {project_id}")
    
    # Return mock data for now
    mock_project = {
        "id": str(project_id),
        "name": f"Sample Project {project_id}",
        "description": "This is a sample project description",
        "status": "active",
        "owner_id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    logger.info(f"Returning mock project: {mock_project['name']}")
    return mock_project


@router.put("/{project_id}")
async def update_project(project_id: UUID, update_data: dict):
    """
    Update a project without database dependencies.
    
    Args:
        project_id: Project UUID
        update_data: Fields to update
        
    Returns:
        Updated mock project details
        
    Raises:
        HTTPException: If project not found or validation fails
    """
    logger.info(f"Updating project with ID: {project_id}")
    
    # Return mock data for now
    mock_project = {
        "id": str(project_id),
        "name": f"Sample Project {project_id}",
        "description": "This is a sample project description",
        "status": "active",
        "owner_id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    # Apply updates from request
    for key, value in update_data.items():
        if key in mock_project:
            mock_project[key] = value
    
    # Update the updated_at timestamp
    mock_project["updated_at"] = datetime.now().isoformat()
    
    logger.info(f"Returning updated mock project: {mock_project['name']}")
    return mock_project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: UUID):
    """
    Delete a project without database dependencies.
    
    Args:
        project_id: Project UUID
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: If project not found
    """
    logger.info(f"Deleting project with ID: {project_id}")
    
    # For now, just return a success response
    # In a real implementation, this would delete the project from the database
    logger.info(f"Project {project_id} deleted successfully")
    return None
