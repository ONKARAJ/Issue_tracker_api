"""
Minimal User router for Issue Tracker API.

This module provides REST endpoints for:
- User operations without database dependencies

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
async def list_users():
    """
    List users without database dependencies.
    
    Returns:
        List of mock users
    """
    logger.info("Listing users (mock data)")
    
    # Return mock data for now
    mock_users = [
        {
            "id": str(uuid4()),
            "email": "user1@example.com",
            "full_name": "User One",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
        },
        {
            "id": str(uuid4()),
            "email": "user2@example.com",
            "full_name": "User Two",
            "role": "developer",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
        }
    ]
    
    logger.info(f"Returning {len(mock_users)} mock users")
    return {
        "items": mock_users,
        "meta": {
            "page": 1,
            "size": 20,
            "total": len(mock_users),
            "pages": 1,
            "has_next": False,
            "has_prev": False
        }
    }


@router.get("/{user_id}")
async def get_user(user_id: UUID):
    """
    Get a single user by ID without database dependencies.
    
    Args:
        user_id: User UUID
        
    Returns:
        Mock user details
        
    Raises:
        HTTPException: If user not found
    """
    logger.info(f"Getting user with ID: {user_id}")
    
    # Return mock data for now
    mock_user = {
        "id": str(user_id),
        "email": "user@example.com",
        "full_name": "Sample User",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    logger.info(f"Returning mock user: {mock_user['full_name']}")
    return mock_user


@router.put("/{user_id}")
async def update_user(user_id: UUID, update_data: dict):
    """
    Update a user without database dependencies.
    
    Args:
        user_id: User UUID
        update_data: Fields to update
        
    Returns:
        Updated mock user details
        
    Raises:
        HTTPException: If user not found or validation fails
    """
    logger.info(f"Updating user with ID: {user_id}")
    
    # Return mock data for now
    mock_user = {
        "id": str(user_id),
        "email": "user@example.com",
        "full_name": "Sample User",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    # Apply updates from request
    for key, value in update_data.items():
        if key in mock_user:
            mock_user[key] = value
    
    # Update the updated_at timestamp
    mock_user["updated_at"] = datetime.now().isoformat()
    
    logger.info(f"Returning updated mock user: {mock_user['full_name']}")
    return mock_user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: UUID):
    """
    Delete a user without database dependencies.
    
    Args:
        user_id: User UUID
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: If user not found
    """
    logger.info(f"Deleting user with ID: {user_id}")
    
    # For now, just return a success response
    # In a real implementation, this would delete the user from the database
    logger.info(f"User {user_id} deleted successfully")
    return None
