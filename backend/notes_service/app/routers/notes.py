from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import models, schemas, database
import sys
sys.path.append('/app')
from ..shared.jwt_utils import get_current_user_id
from ..shared.event_schemas import NoteCreatedEvent, NoteUpdatedEvent, NoteDeletedEvent
from ..shared.rabbitmq_client import RabbitMQClient, NOTES_EXCHANGE

router = APIRouter()

# Initialize RabbitMQ client
rabbitmq_client = RabbitMQClient()

# ============================================
# NOTE CRUD ENDPOINTS
# ============================================

@router.post("/", response_model=schemas.NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: schemas.NoteCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Create a new note for the authenticated user"""
    db_note = models.Note(
        title=note.title,
        content=note.content,
        user_id=user_id
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    # Publish note created event
    try:
        event = NoteCreatedEvent(
            note_id=db_note.id,
            user_id=user_id,
            title=db_note.title,
            timestamp=datetime.utcnow()
        )
        rabbitmq_client.publish(NOTES_EXCHANGE, event)
    except Exception as e:
        print(f"Failed to publish note created event: {e}")

    return db_note

@router.get("/", response_model=List[schemas.NoteResponse])
async def read_notes(
    skip: int = 0,
    limit: int = 100,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Get all notes for the authenticated user"""
    notes = db.query(models.Note).filter(
        models.Note.user_id == user_id
    ).offset(skip).limit(limit).all()

    return notes

@router.get("/{note_id}", response_model=schemas.NoteResponse)
async def read_note(
    note_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Get a specific note by ID (must belong to authenticated user)"""
    note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == user_id
    ).first()

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    return note

@router.put("/{note_id}", response_model=schemas.NoteResponse)
async def update_note(
    note_id: int,
    note_update: schemas.NoteUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Update a note (must belong to authenticated user)"""
    db_note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == user_id
    ).first()

    if db_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Update fields if provided
    if note_update.title is not None:
        db_note.title = note_update.title

    if note_update.content is not None:
        db_note.content = note_update.content

    db.commit()
    db.refresh(db_note)

    # Publish note updated event
    try:
        event = NoteUpdatedEvent(
            note_id=db_note.id,
            user_id=user_id,
            title=db_note.title,
            timestamp=datetime.utcnow()
        )
        rabbitmq_client.publish(NOTES_EXCHANGE, event)
    except Exception as e:
        print(f"Failed to publish note updated event: {e}")

    return db_note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Delete a note (must belong to authenticated user)"""
    db_note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == user_id
    ).first()

    if db_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    # Publish note deleted event before deleting
    try:
        event = NoteDeletedEvent(
            note_id=db_note.id,
            user_id=user_id,
            timestamp=datetime.utcnow()
        )
        rabbitmq_client.publish(NOTES_EXCHANGE, event)
    except Exception as e:
        print(f"Failed to publish note deleted event: {e}")

    db.delete(db_note)
    db.commit()

    return None 