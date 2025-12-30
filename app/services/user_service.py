"""
User service for Issue Tracker API.

This module provides business logic for:
- User CRUD operations
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse, UserList
from app.schemas.common import PaginatedResponse
from .base_service import BaseService


class UserService(BaseService[User]):
    """
    Service class for user business logic.

    Provides user management operations.
    """

    def __init__(self, db: Session):
        """Initialize user service."""
        super().__init__(db, User)

    def get_user(self, user_id: UUID) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            user_id: User UUID

        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """
        Update user information.

        Args:
            user_id: User UUID
            user_data: Updated user data

        Returns:
            Updated user instance or None if not found
        """
        user = self.get_user(user_id)
        if not user:
            return None

        update_data = user_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            raise ValueError("Failed to update user")

    def delete_user(self, user_id: UUID) -> bool:
        """
        Soft delete a user.

        Args:
            user_id: User UUID

        Returns:
            True if deleted, False if not found
        """
        user = self.get_user(user_id)
        if not user:
            return False

        # Soft delete by setting is_active to False
        user.is_active = False
        self.db.commit()
        return True

    def list_users(self, page: int = 1, size: int = 20) -> PaginatedResponse[List[UserList]]:
        """
        List users with pagination.

        Args:
            page: Page number
            size: Items per page

        Returns:
            Paginated response with user list
        """
        query = self.db.query(User).filter(User.is_active == True)
        return self._paginate_query(query, page, size, UserList)
