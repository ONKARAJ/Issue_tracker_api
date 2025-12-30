"""
Pydantic schemas for User entity.

This module provides schemas for:
- User updates
- User responses with relationships
- Input validation and serialization
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole


class UserBase(BaseModel):
    """
    Base user schema with common fields.
    """
    
    email: EmailStr = Field(description="User's unique email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    role: UserRole = Field(default=UserRole.DEVELOPER, description="User role")
    is_active: bool = Field(default=True, description="Whether the user account is active")


class UserUpdate(BaseModel):
    """
    Schema for user update requests.
    
    All fields are optional to allow partial updates.
    """
    
    email: Optional[EmailStr] = Field(None, description="User's email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User's full name")
    role: Optional[UserRole] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Whether the user account is active")


class UserResponse(UserBase):
    """
    Schema for user responses.
    
    Excludes sensitive information like password hash.
    """
    
    id: UUID = Field(description="User's unique identifier")
    version: int = Field(description="Version for optimistic concurrency control")
    created_at: datetime = Field(description="Timestamp when user was created")
    updated_at: datetime = Field(description="Timestamp when user was last updated")
    is_deleted: bool = Field(description="Whether the user is soft-deleted")
    
    class Config:
        from_attributes = True


class UserList(BaseModel):
    """
    Schema for user list responses.
    
    Used in paginated responses.
    """
    
    id: UUID = Field(description="User's unique identifier")
    email: EmailStr = Field(description="User's email address")
    full_name: str = Field(description="User's full name")
    role: UserRole = Field(description="User role")
    is_active: bool = Field(description="Whether the user account is active")
    created_at: datetime = Field(description="Timestamp when user was created")
    
    class Config:
        from_attributes = True
