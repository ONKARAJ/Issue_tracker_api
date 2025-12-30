"""
Timeline service for Issue Tracker API.

This module provides business logic for:
- Issue timeline generation
- Activity tracking
- Chronological event ordering
- History reconstruction
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.models.issue import Issue
from app.models.comment import Comment
from app.models.user import User


class TimelineService:
    """
    Service class for generating issue timelines.
    
    Provides timeline operations with:
- Event reconstruction from existing data
- Chronological ordering
- Actor resolution
- Event type classification
    """
    
    def __init__(self, db: Session):
        """Initialize timeline service."""
        self.db = db
    
    def get_issue_timeline(self, issue_id: UUID) -> Dict[str, Any]:
        """
        Get chronological history for an issue.
        
        Args:
            issue_id: Issue UUID
            
        Returns:
            Timeline with all events in chronological order
            
        Raises:
            ValueError: If issue not found
        """
        # Verify issue exists
        issue = self.db.query(Issue).filter(
            and_(
                Issue.id == issue_id,
                Issue.is_deleted == False
            )
        ).first()
        
        if not issue:
            raise ValueError("Issue not found")
        
        events = []
        
        # Add issue creation event
        creator = self.db.query(User).filter(User.id == issue.creator_id).first()
        events.append({
            'id': f"issue_created_{issue.id}",
            'event_type': 'created',
            'timestamp': issue.created_at,
            'actor_id': issue.creator_id,
            'actor_name': creator.full_name if creator else 'Unknown',
            'details': f"Issue '{issue.title}' was created",
            'metadata': {
                'issue_title': issue.title,
                'initial_status': issue.status.value,
                'initial_priority': issue.priority.value
            }
        })
        
        # Add comment events
        comments = self.db.query(Comment).filter(
            and_(
                Comment.issue_id == issue_id,
                Comment.is_deleted == False
            )
        ).order_by(Comment.created_at.asc()).all()
        
        for comment in comments:
            author = self.db.query(User).filter(User.id == comment.author_id).first()
            events.append({
                'id': f"comment_{comment.id}",
                'event_type': 'commented',
                'timestamp': comment.created_at,
                'actor_id': comment.author_id,
                'actor_name': author.full_name if author else 'Unknown',
                'details': f"Added comment: {comment.content[:100]}{'...' if len(comment.content) > 100 else ''}",
                'metadata': {
                    'comment_id': comment.id,
                    'comment_content': comment.content
                }
            })
        
        # Add status change events (inferred from current state)
        # In a real implementation, you'd have a history table
        # For now, we'll add the current status as an event
        if issue.status.value != 'open':
            events.append({
                'id': f"status_change_{issue.id}",
                'event_type': 'status_changed',
                'timestamp': issue.updated_at,
                'actor_id': issue.assignee_id,  # Inferred - would be from history
                'actor_name': 'Unknown',  # Would be resolved from history
                'details': f"Status changed to {issue.status.value}",
                'metadata': {
                    'old_status': 'open',  # Inferred - would be from history
                    'new_status': issue.status.value
                }
            })
        
        # Add assignment events (inferred)
        if issue.assignee_id and issue.assignee_id != issue.creator_id:
            assignee = self.db.query(User).filter(User.id == issue.assignee_id).first()
            events.append({
                'id': f"assigned_{issue.id}",
                'event_type': 'assigned',
                'timestamp': issue.created_at,  # Inferred - would be from history
                'actor_id': issue.creator_id,
                'actor_name': creator.full_name if creator else 'Unknown',
                'details': f"Assigned to {assignee.full_name if assignee else 'Unknown'}",
                'metadata': {
                    'assignee_id': issue.assignee_id,
                    'assignee_name': assignee.full_name if assignee else 'Unknown'
                }
            })
        
        # Sort events chronologically
        events.sort(key=lambda x: x['timestamp'])
        
        return {
            'issue_id': issue_id,
            'events': events,
            'total_events': len(events)
        }
