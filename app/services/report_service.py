"""
Report service for Issue Tracker API.

This module provides business logic for:
- Top assignees reporting
- Issue latency reporting
- Performance metrics
- Data aggregation
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.models.issue import Issue, IssueStatus
from app.models.user import User


class ReportService:
    """
    Service class for generating reports and analytics.
    
    Provides reporting operations with:
- Efficient aggregation queries
- Performance optimization
- Data validation
- Flexible filtering
    """
    
    def __init__(self, db: Session):
        """Initialize report service."""
        self.db = db
    
    def get_top_assignees(self, limit: int = 10, project_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """
        Get assignees ordered by number of assigned issues.
        
        Args:
            limit: Maximum number of assignees to return
            project_id: Optional project filter
            
        Returns:
            List of assignees with issue counts
        """
        # Build base query
        query = self.db.query(
            User.id,
            User.full_name,
            User.email,
            func.count(Issue.id).label('issue_count')
        ).join(
            Issue, User.id == Issue.assignee_id
        ).filter(
            and_(
                Issue.is_deleted == False,
                User.is_deleted == False,
                User.is_active == True
            )
        )
        
        # Apply project filter if provided
        if project_id:
            query = query.filter(Issue.project_id == project_id)
        
        # Group and order
        results = query.group_by(
            User.id, User.full_name, User.email
        ).order_by(
            desc('issue_count')
        ).limit(limit).all()
        
        return [
            {
                'user_id': result.id,
                'full_name': result.full_name,
                'email': result.email,
                'issue_count': result.issue_count
            }
            for result in results
        ]
    
    def get_resolution_latency(self, days: int = 30, project_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Get average resolution time for resolved issues.
        
        Args:
            days: Number of days to look back
            project_id: Optional project filter
            
        Returns:
            Dictionary with latency statistics
        """
        # Calculate date threshold
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Build base query for resolved issues
        query = self.db.query(
            func.avg(
                func.extract('epoch', Issue.updated_at - Issue.created_at)
            ).label('avg_resolution_time_seconds'),
            func.count(Issue.id).label('resolved_count'),
            func.min(
                func.extract('epoch', Issue.updated_at - Issue.created_at)
            ).label('min_resolution_time_seconds'),
            func.max(
                func.extract('epoch', Issue.updated_at - Issue.created_at)
            ).label('max_resolution_time_seconds')
        ).filter(
            and_(
                Issue.is_deleted == False,
                Issue.status.in_([IssueStatus.RESOLVED, IssueStatus.CLOSED]),
                Issue.updated_at >= since_date
            )
        )
        
        # Apply project filter if provided
        if project_id:
            query = query.filter(Issue.project_id == project_id)
        
        result = query.first()
        
        if not result or result.resolved_count == 0:
            return {
                'average_resolution_hours': 0,
                'resolved_count': 0,
                'min_resolution_hours': 0,
                'max_resolution_hours': 0,
                'period_days': days
            }
        
        return {
            'average_resolution_hours': round(result.avg_resolution_time_seconds / 3600, 2),
            'resolved_count': result.resolved_count,
            'min_resolution_hours': round(result.min_resolution_time_seconds / 3600, 2),
            'max_resolution_hours': round(result.max_resolution_time_seconds / 3600, 2),
            'period_days': days
        }
    
    def get_issue_velocity(self, days: int = 30, project_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Get issue creation and resolution velocity.
        
        Args:
            days: Number of days to look back
            project_id: Optional project filter
            
        Returns:
            Dictionary with velocity metrics
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Query for created issues
        created_query = self.db.query(func.count(Issue.id)).filter(
            and_(
                Issue.is_deleted == False,
                Issue.created_at >= since_date
            )
        )
        
        # Query for resolved issues
        resolved_query = self.db.query(func.count(Issue.id)).filter(
            and_(
                Issue.is_deleted == False,
                Issue.status.in_([IssueStatus.RESOLVED, IssueStatus.CLOSED]),
                Issue.updated_at >= since_date
            )
        )
        
        # Apply project filter if provided
        if project_id:
            created_query = created_query.filter(Issue.project_id == project_id)
            resolved_query = resolved_query.filter(Issue.project_id == project_id)
        
        created_count = created_query.scalar() or 0
        resolved_count = resolved_query.scalar() or 0
        
        return {
            'created_count': created_count,
            'resolved_count': resolved_count,
            'net_change': created_count - resolved_count,
            'period_days': days,
            'daily_creation_rate': round(created_count / days, 2),
            'daily_resolution_rate': round(resolved_count / days, 2)
        }
