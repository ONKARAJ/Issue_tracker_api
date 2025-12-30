"""
Issue service for Issue Tracker API.

This module provides business logic for:
- Issue CRUD operations
- Issue workflow management
- Issue assignment and status transitions
- Issue filtering and search
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, Dict, Any, List
from uuid import UUID

from app.models.issue import Issue, IssueStatus, IssueType, IssuePriority
from app.models.project import Project
from app.models.user import User
from app.models.comment import Comment
from app.models.label import Label
from app.models.issue_label import IssueLabel
from app.schemas.issue import IssueCreate, IssueUpdate
from app.schemas.common import PaginatedResponse
from .base_service import BaseService

# Set up logging
logger = logging.getLogger(__name__)


class IssueService(BaseService[Issue]):
    """
    Service class for issue business logic.
    
    Provides issue management operations with:
    - Workflow state management
    - Assignment validation
    - Project relationship validation
    - Status transition validation
    """
    
    def __init__(self, db: Session):
        """Initialize issue service."""
        super().__init__(db, Issue)
    
    def create_issue(self, issue_data: IssueCreate) -> Issue:
        """
        Create a new issue with validation.
        
        Args:
            issue_data: Issue creation data
            
        Returns:
            Created issue instance
            
        Raises:
            ValueError: If validation fails
        """
        # Verify project exists and is active
        project = self.db.query(Project).filter(
            and_(
                Project.id == issue_data.project_id,
                Project.is_deleted == False
            )
        ).first()
        
        if not project:
            raise ValueError("Project not found")
        
        if not project.can_add_issues():
            raise ValueError("Cannot add issues to this project in current status")
        
        # Verify creator exists and is active
        creator = self.db.query(User).filter(
            and_(
                User.id == issue_data.creator_id,
                User.is_deleted == False,
                User.is_active == True
            )
        ).first()
        
        if not creator:
            raise ValueError("Creator not found or inactive")
        
        # Validate assignee exists if provided
        if issue_data.assignee_id:
            assignee = self.db.query(User).filter(
                and_(
                    User.id == issue_data.assignee_id,
                    User.is_deleted == False,
                    User.is_active == True
                )
            ).first()
            
            if not assignee:
                raise ValueError("Assignee not found or inactive")
        
        # Create issue with version = 1
        issue_dict = issue_data.dict()
        issue_dict['version'] = 1  # Set initial version
        
        return self.create(issue_dict)
    
    def get_issue_with_details(self, issue_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get issue details with associated comments and labels.
        
        Args:
            issue_id: Issue UUID
            
        Returns:
            Dictionary with issue details, comments, and labels
            
        Raises:
            ValueError: If issue not found
        """
        # Get issue
        issue = self.get_issue(issue_id)
        if not issue:
            return None
        
        # Get associated comments
        comments = self.db.query(Comment).filter(
            and_(
                Comment.issue_id == issue_id,
                Comment.is_deleted == False
            )
        ).order_by(Comment.created_at.asc()).all()
        
        # Get associated labels
        labels = self.db.query(Label).join(IssueLabel).filter(
            and_(
                IssueLabel.issue_id == issue_id,
                Label.is_deleted == False
            )
        ).order_by(Label.name).all()
        
        return {
            'issue': issue,
            'comments': comments,
            'labels': labels
        }
    
    def get_issue(self, issue_id: UUID) -> Optional[Issue]:
        """
        Get issue by ID.
        
        Args:
            issue_id: Issue UUID
            
        Returns:
            Issue instance or None
        """
        return self.get_by_id(str(issue_id))
    
    def update_issue_with_optimistic_locking(self, issue_id: UUID, update_data: Dict[str, Any]) -> Optional[Issue]:
        """
        Update issue with optimistic concurrency control.
        
        Args:
            issue_id: Issue UUID
            update_data: Issue update data with version
            
        Returns:
            Updated issue or None
            
        Raises:
            ValueError: If version mismatch or validation fails
        """
        issue = self.get_issue(issue_id)
        if not issue:
            return None
        
        # Check version for optimistic concurrency control
        expected_version = update_data.get('version')
        if expected_version is None:
            raise ValueError("Version field is required for updates")
        
        if issue.version != expected_version:
            raise ValueError(f"Version conflict: expected {expected_version}, got {issue.version}")
        
        # Validate assignee if being updated
        if 'assignee_id' in update_data and update_data['assignee_id']:
            assignee = self.db.query(User).filter(
                and_(
                    User.id == update_data['assignee_id'],
                    User.is_deleted == False,
                    User.is_active == True
                )
            ).first()
            
            if not assignee:
                raise ValueError("Assignee not found or inactive")
        
        # Validate status transition if being updated
        if 'status' in update_data and update_data['status'] != issue.status:
            if not issue.can_transition_to(update_data['status']):
                raise ValueError(f"Cannot transition from {issue.status} to {update_data['status']}")
        
        # Update fields (excluding version)
        update_fields = {k: v for k, v in update_data.items() if k != 'version'}
        
        # Apply updates
        for field, value in update_fields.items():
            if hasattr(issue, field):
                setattr(issue, field, value)
        
        # Increment version
        issue.increment_version()
        
        self.db.commit()
        self.db.refresh(issue)
        return issue
    
    def update_issue(self, issue_id: UUID, issue_data: IssueUpdate) -> Optional[Issue]:
        """
        Update issue with validation.
        
        Args:
            issue_id: Issue UUID
            issue_data: Issue update data
            
        Returns:
            Updated issue or None
            
        Raises:
            ValueError: If validation fails
        """
        issue = self.get_issue(issue_id)
        if not issue:
            return None
        
        # Check name uniqueness if being updated
        if issue_data.title and issue_data.title != issue.title:
            existing_issue = self.db.query(Issue).filter(
                and_(
                    Issue.title == issue_data.title,
                    Issue.project_id == issue.project_id,
                    Issue.id != issue_id,
                    Issue.is_deleted == False
                )
            ).first()
            
            if existing_issue:
                raise ValueError(f"Issue with title '{issue_data.title}' already exists in this project")
        
        # Validate assignee if being updated
        if issue_data.assignee_id:
            assignee = self.db.query(User).filter(
                and_(
                    User.id == issue_data.assignee_id,
                    User.is_deleted == False,
                    User.is_active == True
                )
            ).first()
            
            if not assignee:
                raise ValueError("Assignee not found or inactive")
        
        # Validate status transition if being updated
        if issue_data.status and issue_data.status != issue.status:
            if not issue.can_transition_to(issue_data.status):
                raise ValueError(f"Cannot transition from {issue.status} to {issue_data.status}")
        
        # Prepare update data
        update_dict = issue_data.dict(exclude_unset=True)
        return self.update(str(issue_id), update_dict)
    
    def update_issue_status(self, issue_id: UUID, new_status: IssueStatus) -> Optional[Issue]:
        """
        Update issue status with workflow validation.
        
        Args:
            issue_id: Issue UUID
            new_status: New issue status
            
        Returns:
            Updated issue or None
            
        Raises:
            ValueError: If status transition is invalid
        """
        issue = self.get_issue(issue_id)
        if not issue:
            return None
        
        if not issue.can_transition_to(new_status):
            raise ValueError(f"Cannot transition from {issue.status} to {new_status}")
        
        return self.update(str(issue_id), {'status': new_status})
    
    def delete_issue(self, issue_id: UUID) -> bool:
        """
        Soft delete issue.
        
        Args:
            issue_id: Issue UUID
            
        Returns:
            True if deleted, False if not found
        """
        return self.soft_delete(str(issue_id))
    
    def list_issues(
        self,
        page: int = 1,
        size: int = 20,
        project_id: Optional[UUID] = None,
        status: Optional[str] = None,
        assignee_id: Optional[UUID] = None,
    ) -> PaginatedResponse:
        """
        List issues with filtering and pagination.
        
        Args:
            page: Page number
            size: Items per page
            project_id: Optional project filter
            status: Optional status filter
            assignee_id: Optional assignee filter
            
        Returns:
            Paginated list of issues
        """
        logger.info(f"Listing issues with page={page}, size={size}, project_id={project_id}, status={status}, assignee_id={assignee_id}")
        
        try:
            # Build base query with filters
            logger.info("Building base query with filters")
            query = self.db.query(Issue).filter(Issue.is_deleted == False)
            
            # Apply filters
            if project_id:
                logger.info(f"Applying project_id filter: {project_id}")
                query = query.filter(Issue.project_id == project_id)
            
            if status:
                logger.info(f"Applying status filter: {status}")
                try:
                    status_enum = IssueStatus(status)
                    query = query.filter(Issue.status == status_enum)
                except ValueError:
                    logger.error(f"Invalid status: {status}")
                    raise ValueError(f"Invalid status: {status}")
            
            if assignee_id:
                logger.info(f"Applying assignee_id filter: {assignee_id}")
                query = query.filter(Issue.assignee_id == assignee_id)
            
            # Order by created_at descending for most recent first
            logger.info("Ordering by created_at descending")
            query = query.order_by(Issue.created_at.desc())
            
            # Get total count
            logger.info("Getting total count")
            total = query.count()
            logger.info(f"Total count: {total}")
            
            # Apply pagination
            from math import ceil
            offset = (page - 1) * size
            logger.info(f"Applying pagination: offset={offset}, limit={size}")
            items = query.offset(offset).limit(size).all()
            logger.info(f"Retrieved {len(items)} items")
            
            # Calculate pagination metadata
            pages = ceil(total / size) if size > 0 else 0
            has_next = page < pages
            has_prev = page > 1
            
            from app.schemas.common import PaginationMeta
            meta = PaginationMeta(
                page=page,
                size=size,
                total=total,
                pages=pages,
                has_next=has_next,
                has_prev=has_prev
            )
            
            logger.info(f"Returning paginated response with {len(items)} items")
            return PaginatedResponse(items=items, meta=meta)
            
        except Exception as e:
            logger.error(f"Error in list_issues: {str(e)}")
            raise
    
    def list_project_issues(self, project_id: UUID, page: int = 1, size: int = 20) -> PaginatedResponse:
        """
        List issues for a specific project.
        
        Args:
            project_id: Project UUID
            page: Page number
            size: Items per page
            
        Returns:
            Paginated list of project issues
        """
        return self.list_issues(page=page, size=size, project_id=project_id)
    
    def list_user_assigned_issues(self, user_id: UUID, page: int = 1, size: int = 20) -> PaginatedResponse:
        """
        List issues assigned to a specific user.
        
        Args:
            user_id: User UUID
            page: Page number
            size: Items per page
            
        Returns:
            Paginated list of assigned issues
        """
        return self.list_issues(page=page, size=size, assignee_id=user_id)
    
    def list_user_created_issues(self, user_id: UUID, page: int = 1, size: int = 20) -> PaginatedResponse:
        """
        List issues created by a specific user.
        
        Args:
            user_id: User UUID
            page: Page number
            size: Items per page
            
        Returns:
            Paginated list of created issues
        """
        filters = {'creator_id': user_id}
        return self.get_all(page=page, size=size, filters=filters, order_by='created_at', order_desc=True)
    
    def search_issues(self, query: str, page: int = 1, size: int = 20) -> PaginatedResponse:
        """
        Search issues by title or description.
        
        Args:
            query: Search query
            page: Page number
            size: Items per page
            
        Returns:
            Paginated list of matching issues
        """
        # Build search query
        search_filter = or_(
            Issue.title.ilike(f"%{query}%"),
            Issue.description.ilike(f"%{query}%")
        )
        
        query = self.db.query(Issue).filter(
            and_(
                Issue.is_deleted == False,
                search_filter
            )
        ).order_by(Issue.created_at.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        items = query.offset(offset).limit(size).all()
        
        # Calculate pagination metadata
        from math import ceil
        pages = ceil(total / size) if size > 0 else 0
        has_next = page < pages
        has_prev = page > 1
        
        from app.schemas.common import PaginationMeta
        meta = PaginationMeta(
            page=page,
            size=size,
            total=total,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return PaginatedResponse(items=items, meta=meta)
    
    def bulk_update_status_transactional(self, issue_ids: List[UUID], new_status: IssueStatus) -> Dict[str, Any]:
        """
        Update status for multiple issues in a single transaction.
        
        Args:
            issue_ids: List of issue UUIDs to update
            new_status: New status to apply
            
        Returns:
            Dictionary with success/failure counts and errors
            
        Raises:
            ValueError: If validation fails for any issue
        """
        from app.database import DatabaseTransaction
        
        # Validate all issues exist and can transition
        issues = self.db.query(Issue).filter(
            and_(
                Issue.id.in_(issue_ids),
                Issue.is_deleted == False
            )
        ).all()
        
        if len(issues) != len(issue_ids):
            found_ids = [issue.id for issue in issues]
            missing_ids = [iid for iid in issue_ids if iid not in found_ids]
            raise ValueError(f"Issues not found: {missing_ids}")
        
        # Validate status transitions for all issues
        validation_errors = []
        for issue in issues:
            if not issue.can_transition_to(new_status):
                validation_errors.append({
                    'issue_id': issue.id,
                    'error': f"Cannot transition from {issue.status} to {new_status}"
                })
        
        if validation_errors:
            raise ValueError(f"Status transition validation failed: {validation_errors}")
        
        # Perform atomic update in single transaction
        try:
            with DatabaseTransaction(self.db) as db:
                # Update all issues
                updated_count = db.query(Issue).filter(
                    Issue.id.in_(issue_ids)
                ).update({
                    'status': new_status,
                    'version': Issue.version + 1
                }, synchronize_session=False)
                
                return {
                    'success_count': updated_count,
                    'failure_count': 0,
                    'errors': [],
                    'message': f"Successfully updated {updated_count} issues to {new_status}"
                }
        except Exception as e:
            # Transaction will be rolled back automatically
            raise ValueError(f"Bulk update failed: {str(e)}")
    
    def import_issues_from_csv(self, csv_content: str, creator_id: UUID) -> Dict[str, Any]:
        """
        Import issues from CSV content.
        
        Args:
            csv_content: Raw CSV content as string
            creator_id: UUID of the user creating the issues
            
        Returns:
            Dictionary with import results and errors
            
        Raises:
            ValueError: If CSV format is invalid
        """
        import csv
        import io
        from app.database import DatabaseTransaction
        
        # Parse CSV
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        # Validate required columns
        required_columns = ['title', 'project_id']
        if not all(col in reader.fieldnames for col in required_columns):
            missing_cols = [col for col in required_columns if col not in reader.fieldnames]
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        created_issues = []
        errors = []
        row_number = 2  # Start after header
        
        # Validate all rows first
        validated_rows = []
        for row in reader:
            try:
                # Validate required fields
                if not row.get('title') or not row['title'].strip():
                    errors.append({
                        'row_number': row_number,
                        'field': 'title',
                        'value': row.get('title', ''),
                        'error': 'Title is required',
                        'raw_data': row
                    })
                    row_number += 1
                    continue
                
                # Validate project_id
                try:
                    project_id = UUID(row['project_id'])
                except ValueError:
                    errors.append({
                        'row_number': row_number,
                        'field': 'project_id',
                        'value': row.get('project_id', ''),
                        'error': 'Invalid project_id format',
                        'raw_data': row
                    })
                    row_number += 1
                    continue
                
                # Validate assignee_id if provided
                assignee_id = None
                if row.get('assignee_id') and row['assignee_id'].strip():
                    try:
                        assignee_id = UUID(row['assignee_id'])
                    except ValueError:
                        errors.append({
                            'row_number': row_number,
                            'field': 'assignee_id',
                            'value': row.get('assignee_id', ''),
                            'error': 'Invalid assignee_id format',
                            'raw_data': row
                        })
                        row_number += 1
                        continue
                
                # Validate status if provided
                status = 'open'  # default
                if row.get('status') and row['status'].strip():
                    try:
                        from app.models.issue import IssueStatus
                        status = IssueStatus(row['status'].lower())
                    except ValueError:
                        errors.append({
                            'row_number': row_number,
                            'field': 'status',
                            'value': row.get('status', ''),
                            'error': f"Invalid status. Must be one of: {[s.value for s in IssueStatus]}",
                            'raw_data': row
                        })
                        row_number += 1
                        continue
                
                # Validate priority if provided
                priority = 'medium'  # default
                if row.get('priority') and row['priority'].strip():
                    try:
                        from app.models.issue import IssuePriority
                        priority = IssuePriority(row['priority'].lower())
                    except ValueError:
                        errors.append({
                            'row_number': row_number,
                            'field': 'priority',
                            'value': row.get('priority', ''),
                            'error': f"Invalid priority. Must be one of: {[p.value for p in IssuePriority]}",
                            'raw_data': row
                        })
                        row_number += 1
                        continue
                
                validated_rows.append({
                    'title': row['title'].strip(),
                    'description': row.get('description', '').strip(),
                    'project_id': project_id,
                    'assignee_id': assignee_id,
                    'status': status,
                    'priority': priority,
                    'type': row.get('type', 'task').strip() or 'task'
                })
                
            except Exception as e:
                errors.append({
                    'row_number': row_number,
                    'field': 'general',
                    'value': '',
                    'error': f'Unexpected error: {str(e)}',
                    'raw_data': row
                })
            
            row_number += 1
        
        # Create issues in transaction if validation passed
        if validated_rows and not errors:
            try:
                with DatabaseTransaction(self.db) as db:
                    for row_data in validated_rows:
                        # Verify project exists
                        project = db.query(Project).filter(
                            and_(
                                Project.id == row_data['project_id'],
                                Project.is_deleted == False
                            )
                        ).first()
                        
                        if not project:
                            errors.append({
                                'row_number': 'unknown',
                                'field': 'project_id',
                                'value': str(row_data['project_id']),
                                'error': 'Project not found',
                                'raw_data': row_data
                            })
                            continue
                        
                        # Verify assignee exists if provided
                        if row_data['assignee_id']:
                            assignee = db.query(User).filter(
                                and_(
                                    User.id == row_data['assignee_id'],
                                    User.is_deleted == False,
                                    User.is_active == True
                                )
                            ).first()
                            
                            if not assignee:
                                errors.append({
                                    'row_number': 'unknown',
                                    'field': 'assignee_id',
                                    'value': str(row_data['assignee_id']),
                                    'error': 'Assignee not found or inactive',
                                    'raw_data': row_data
                                })
                                continue
                        
                        # Create issue
                        issue_data = {
                            'title': row_data['title'],
                            'description': row_data['description'],
                            'project_id': row_data['project_id'],
                            'creator_id': creator_id,
                            'assignee_id': row_data['assignee_id'],
                            'status': row_data['status'],
                            'priority': row_data['priority'],
                            'type': row_data['type'],
                            'version': 1
                        }
                        
                        issue = Issue(**issue_data)
                        db.add(issue)
                        created_issues.append(issue)
                
            except Exception as e:
                raise ValueError(f"Failed to create issues: {str(e)}")
        
        total_rows = len(validated_rows) + len(errors)
        
        return {
            'created_count': len(created_issues),
            'failed_count': len(errors),
            'total_rows': total_rows,
            'errors': errors,
            'message': f"Imported {len(created_issues)} issues, {len(errors)} failed"
        }
    
    def get_issue_statistics(self, project_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Get issue statistics.
        
        Args:
            project_id: Optional project filter
            
        Returns:
            Dictionary with issue statistics
        """
        base_query = self.db.query(Issue).filter(Issue.is_deleted == False)
        
        if project_id:
            base_query = base_query.filter(Issue.project_id == project_id)
        
        total_issues = base_query.count()
        open_issues = base_query.filter(Issue.status.in_([IssueStatus.OPEN, IssueStatus.IN_PROGRESS, IssueStatus.IN_REVIEW, IssueStatus.REOPENED])).count()
        closed_issues = base_query.filter(Issue.status.in_([IssueStatus.RESOLVED, IssueStatus.CLOSED])).count()
        
        return {
            'total_issues': total_issues,
            'open_issues': open_issues,
            'closed_issues': closed_issues,
            'resolution_rate': (closed_issues / total_issues * 100) if total_issues > 0 else 0,
        }
