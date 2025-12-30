"""
Pydantic schemas for Issue Tracker API.

This package contains all Pydantic models for:
- Request/response serialization
- Input validation
- Data transformation
- API documentation

Schemas are organized by entity and use naming convention:
- {Entity}Base: Common fields
- {Entity}Create: Creation requests
- {Entity}Update: Update requests
- {Entity}Response: API responses
- {Entity}List: List responses with pagination
"""

from .user import (
    UserBase,
    UserUpdate,
    UserResponse,
    UserList,
)
from .project import (
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectList,
)
from .issue import (
    IssueBase,
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueList,
    IssueStatusUpdate,
)
from .comment import (
    CommentBase,
    CommentCreate,
    CommentResponse,
    CommentList,
)
from .label import (
    LabelBase,
    LabelCreate,
    LabelResponse,
    LabelList,
)
from .common import (
    PaginationParams,
    PaginatedResponse,
    ErrorResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserUpdate",
    "UserResponse",
    "UserList",
    
    # Project schemas
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate", 
    "ProjectResponse",
    "ProjectList",
    
    # Issue schemas
    "IssueBase",
    "IssueCreate",
    "IssueUpdate",
    "IssueResponse",
    "IssueList",
    "IssueStatusUpdate",
    
    # Comment schemas
    "CommentBase",
    "CommentCreate",
    "CommentResponse",
    "CommentList",
    
    # Attachment schemas
    "AttachmentBase",
    "AttachmentResponse",
    "AttachmentList",
    
    # Label schemas
    "LabelBase",
    "LabelCreate",
    "LabelResponse",
    "LabelList",
    
    # Common schemas
    "PaginationParams",
    "PaginatedResponse",
    "ErrorResponse",
]
