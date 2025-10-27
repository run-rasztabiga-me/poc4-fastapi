from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ============================================
# ANALYTICS SCHEMAS
# ============================================

class UserStatisticsResponse(BaseModel):
    user_id: int
    total_notes: int
    total_notes_created: int
    total_notes_updated: int
    total_notes_deleted: int
    total_logins: int
    last_activity: Optional[datetime]
    last_login: Optional[datetime]
    registered_at: Optional[datetime]

    class Config:
        from_attributes = True

class NoteEventResponse(BaseModel):
    id: int
    event_type: str
    note_id: int
    user_id: int
    title: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

class UserEventResponse(BaseModel):
    id: int
    event_type: str
    user_id: int
    username: str
    email: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

class SystemStatistics(BaseModel):
    total_users: int
    total_notes_created: int
    total_notes_updated: int
    total_notes_deleted: int
    total_logins: int
    active_users_today: int
