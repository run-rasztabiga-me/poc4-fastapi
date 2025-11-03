from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ============================================
# USER EVENTS
# ============================================

class UserRegisteredEvent(BaseModel):
    """Event published when a new user registers"""
    event_type: str = "user.registered"
    user_id: int
    username: str
    email: str
    timestamp: datetime

class UserLoggedInEvent(BaseModel):
    """Event published when a user logs in"""
    event_type: str = "user.logged_in"
    user_id: int
    username: str
    timestamp: datetime

# ============================================
# NOTE EVENTS
# ============================================

class NoteCreatedEvent(BaseModel):
    """Event published when a note is created"""
    event_type: str = "note.created"
    note_id: int
    user_id: int
    title: str
    timestamp: datetime

class NoteUpdatedEvent(BaseModel):
    """Event published when a note is updated"""
    event_type: str = "note.updated"
    note_id: int
    user_id: int
    title: str
    timestamp: datetime

class NoteDeletedEvent(BaseModel):
    """Event published when a note is deleted"""
    event_type: str = "note.deleted"
    note_id: int
    user_id: int
    timestamp: datetime
