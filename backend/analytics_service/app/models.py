from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class NoteEvent(Base):
    """Stores all note-related events"""
    __tablename__ = "note_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # note.created, note.updated, note.deleted
    note_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(100))
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

class UserEvent(Base):
    """Stores all user-related events"""
    __tablename__ = "user_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # user.registered, user.logged_in
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100))
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

class UserStatistics(Base):
    """Aggregated user statistics"""
    __tablename__ = "user_statistics"

    user_id = Column(Integer, primary_key=True, index=True)
    total_notes = Column(Integer, default=0)
    total_notes_created = Column(Integer, default=0)
    total_notes_updated = Column(Integer, default=0)
    total_notes_deleted = Column(Integer, default=0)
    total_logins = Column(Integer, default=0)
    last_activity = Column(DateTime)
    last_login = Column(DateTime)
    registered_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
