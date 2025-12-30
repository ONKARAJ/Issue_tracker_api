"""
FastAPI routers for Issue Tracker API.

This package contains all API route handlers organized by entity:
- issues: Issue CRUD and workflow operations
- users: User management and authentication
- projects: Project management
- comments: Comment operations
- attachments: File upload/download operations

Each router follows REST conventions:
- GET /: List resources with pagination
- GET /{id}: Get single resource
- POST /: Create new resource
- PUT /{id}: Update entire resource
- PATCH /{id}: Partial update
- DELETE /{id}: Soft delete resource
"""

from .issues import router as issues
from .users import router as users
from .projects import router as projects
from .comments import router as comments
from .attachments import router as attachments

__all__ = [
    "issues",
    "users", 
    "projects",
    "comments",
    "attachments",
]
