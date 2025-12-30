"""
SQLAlchemy models for Issue Tracker API.

This package contains all database models organized by entity:
- user: User accounts and authentication
- project: Project containers
- issue: Issue tracking with workflow
- comment: Issue discussions
- label: Issue categorization
- issue_label: Many-to-many relationships
- attachment: File uploads
"""

from .base import Base
from .user import User, UserRole
from .project import Project, ProjectStatus
from .issue import Issue, IssueStatus, IssueType, IssuePriority
from .comment import Comment
from .label import Label
from .issue_label import IssueLabel
from .attachment import Attachment

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Project",
    "ProjectStatus",
    "Issue",
    "IssueStatus",
    "IssueType",
    "IssuePriority",
    "Comment",
    "Label",
    "IssueLabel",
    "Attachment",
]