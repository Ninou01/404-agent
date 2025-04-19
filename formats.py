from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StatusTransition(BaseModel):
    from_status: Optional[str] = Field(None, description="Pre-action status, including intra-status if available")
    to_status: Optional[str] = Field(None, description="Post-action status, including intra-status if available")


class TimelineEntry(BaseModel):
    timestamp: datetime
    action: str
    user: str
    location: Optional[str] = None
    status_transition: Optional[StatusTransition] = None
    note: Optional[str] = None
    related_entities: Optional[List[str]] = Field(default_factory=list)


class OrderTimeline(BaseModel):
    order_id: int
    timeline: List[TimelineEntry]


class OrderCurrentState(BaseModel):
    order_id: int
    current_status: Optional[str] = Field(None, description="Main status of the order")
    current_intra_status: Optional[str] = Field(None, description="Intra-status if available")
    last_action: Optional[str] = Field(None, description="The last recorded action on the order")
    last_user: Optional[str] = Field(None, description="Who performed the last action")
    last_user_role: Optional[str] = Field(None, description="The role of the last user")
    location: Optional[str] = Field(None, description="Last known warehouse or zone")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of the last action")

class InvestigationResponse(BaseModel):
    summary: str
    gaps_or_broken_steps: Optional[List[str]] = Field(default_factory=list)
    order_timeline: OrderTimeline
    current_state: OrderCurrentState

