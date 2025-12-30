"""
User router for Issue Tracker API.

This module provides REST endpoints for:
- User CRUD operations
- User authentication and authorization
- User role management
- User profile operations

Follows REST conventions with proper HTTP status codes,
error handling, and request validation.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.user import (
    UserUpdate,
    UserResponse,
    UserList,
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[UserList])
async def list_users(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    """
    List users with pagination.
    
    Args:
        pagination: Pagination parameters
        db: Database session
        
    Returns:
        Paginated list of users
    """
    service = UserService(db)
    return service.list_users(page=pagination.page, size=pagination.size)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a single user by ID.
    
    Args:
        user_id: User UUID
        db: Database session
        
    Returns:
        User details
        
    Raises:
        HTTPException: If user not found
    """
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an entire user.
    
    Args:
        user_id: User UUID
        user_data: User update data
        db: Database session
        
    Returns:
        Updated user
        
    Raises:
        HTTPException: If user not found or validation fails
    """
    service = UserService(db)
    try:
        user = service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Soft delete a user.
    
    Args:
        user_id: User UUID
        db: Database session
        
    Raises:
        HTTPException: If user not found
    """
    service = UserService(db)
    success = service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
