from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from .. import models, schemas, database
import sys
sys.path.append('/app')
from shared.jwt_utils import get_current_user_id

router = APIRouter()

# ============================================
# USER STATISTICS ENDPOINTS
# ============================================

@router.get("/users/me/statistics", response_model=schemas.UserStatisticsResponse)
async def get_my_statistics(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Get statistics for the authenticated user"""
    user_stats = db.query(models.UserStatistics).filter(
        models.UserStatistics.user_id == current_user_id
    ).first()

    if not user_stats:
        # Return default statistics if none exist yet
        return schemas.UserStatisticsResponse(
            user_id=current_user_id,
            total_notes=0,
            total_notes_created=0,
            total_notes_updated=0,
            total_notes_deleted=0,
            total_logins=0,
            last_activity=None,
            last_login=None,
            registered_at=None
        )

    return user_stats

@router.get("/users/{user_id}/statistics", response_model=schemas.UserStatisticsResponse)
async def get_user_statistics(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Get statistics for a specific user (must be the authenticated user)"""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own statistics"
        )

    user_stats = db.query(models.UserStatistics).filter(
        models.UserStatistics.user_id == user_id
    ).first()

    if not user_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Statistics not found for this user"
        )

    return user_stats

# ============================================
# EVENT HISTORY ENDPOINTS
# ============================================

@router.get("/users/{user_id}/events/notes", response_model=List[schemas.NoteEventResponse])
async def get_user_note_events(
    user_id: int,
    limit: int = 50,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Get note events for a specific user (must be the authenticated user)"""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own events"
        )

    events = db.query(models.NoteEvent).filter(
        models.NoteEvent.user_id == user_id
    ).order_by(models.NoteEvent.timestamp.desc()).limit(limit).all()

    return events

@router.get("/users/{user_id}/events/activity", response_model=List[schemas.UserEventResponse])
async def get_user_activity_events(
    user_id: int,
    limit: int = 50,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Get user activity events (must be the authenticated user)"""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own events"
        )

    events = db.query(models.UserEvent).filter(
        models.UserEvent.user_id == user_id
    ).order_by(models.UserEvent.timestamp.desc()).limit(limit).all()

    return events

# ============================================
# SYSTEM STATISTICS ENDPOINTS (PUBLIC)
# ============================================

@router.get("/system/statistics", response_model=schemas.SystemStatistics)
async def get_system_statistics(db: Session = Depends(database.get_db)):
    """Get overall system statistics (public endpoint)"""
    # Count total users
    total_users = db.query(func.count(models.UserStatistics.user_id)).scalar() or 0

    # Sum all note statistics
    stats = db.query(
        func.sum(models.UserStatistics.total_notes_created).label("total_created"),
        func.sum(models.UserStatistics.total_notes_updated).label("total_updated"),
        func.sum(models.UserStatistics.total_notes_deleted).label("total_deleted"),
        func.sum(models.UserStatistics.total_logins).label("total_logins")
    ).first()

    # Count active users today
    today = datetime.utcnow().date()
    active_users_today = db.query(func.count(models.UserStatistics.user_id)).filter(
        func.date(models.UserStatistics.last_activity) == today
    ).scalar() or 0

    return schemas.SystemStatistics(
        total_users=total_users,
        total_notes_created=stats.total_created or 0,
        total_notes_updated=stats.total_updated or 0,
        total_notes_deleted=stats.total_deleted or 0,
        total_logins=stats.total_logins or 0,
        active_users_today=active_users_today
    )

@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
