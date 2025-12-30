"""
Pydantic schemas for timeline operations.

This module provides schemas for:
- Timeline events
- Issue history
- Chronological activity tracking
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID


class TimelineEvent(BaseModel):
    """
    Schema for individual timeline events.
    
    Attributes:
        id: Event identifier
        event_type: Type of event (created, status_changed, commented)
        timestamp: When the event occurred
        actor_id: User who performed the action
        actor_name: Name of the user who performed the action
        details: Event-specific details
        metadata: Additional event metadata
    """
    
    id: str = Field(description="Event identifier")
    event_type: str = Field(description="Type of event")
    timestamp: datetime = Field(description="When the event occurred")
    actor_id: Optional[UUID] = Field(None, description="User who performed the action")
    actor_name: Optional[str] = Field(None, description="Name of the user who performed the action")
    details: str = Field(description="Event description")
    metadata: Optional[dict] = Field(None, description="Additional event metadata")


class TimelineResponse(BaseModel):
    """
    Schema for timeline responses.
    
    Attributes:
        issue_id: Issue UUID
        events: Chronological list of events
        total_events: Total number of events
    """
    
    issue_id: UUID = Field(description="Issue UUID")
    events: List[TimelineEvent] = Field(description="Chronological list of events")
    total_events: int = Field(description="Total number of events")
