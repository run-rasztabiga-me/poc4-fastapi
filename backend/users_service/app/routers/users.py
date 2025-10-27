from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import models, schemas, database, auth
import sys
sys.path.append('/app')
from shared.jwt_utils import create_access_token, get_current_user_id
from shared.event_schemas import UserRegisteredEvent, UserLoggedInEvent
from shared.rabbitmq_client import RabbitMQClient, USERS_EXCHANGE

router = APIRouter()

# Initialize RabbitMQ client
rabbitmq_client = RabbitMQClient()

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Register a new user"""
    # Check if username already exists
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Publish user registered event
    try:
        event = UserRegisteredEvent(
            user_id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            timestamp=datetime.utcnow()
        )
        rabbitmq_client.publish(USERS_EXCHANGE, event)
    except Exception as e:
        print(f"Failed to publish user registered event: {e}")

    return db_user

@router.post("/login", response_model=schemas.Token)
async def login(user_login: schemas.UserLogin, db: Session = Depends(database.get_db)):
    """Login user and return JWT token"""
    user = auth.authenticate_user(db, user_login.username, user_login.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.id})

    # Publish user logged in event
    try:
        event = UserLoggedInEvent(
            user_id=user.id,
            username=user.username,
            timestamp=datetime.utcnow()
        )
        rabbitmq_client.publish(USERS_EXCHANGE, event)
    except Exception as e:
        print(f"Failed to publish user logged in event: {e}")

    return {"access_token": access_token, "token_type": "bearer"}

# ============================================
# USER MANAGEMENT ENDPOINTS
# ============================================

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Get current authenticated user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: Session = Depends(database.get_db)):
    """Get user by ID (public endpoint for inter-service communication)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get list of users (requires authentication)"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.put("/me", response_model=schemas.UserResponse)
async def update_current_user(
    user_update: schemas.UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Update current authenticated user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields if provided
    if user_update.username is not None:
        # Check if new username is already taken
        existing = db.query(models.User).filter(
            models.User.username == user_update.username,
            models.User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.username = user_update.username

    if user_update.email is not None:
        # Check if new email is already taken
        existing = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
        user.email = user_update.email

    if user_update.password is not None:
        user.hashed_password = auth.get_password_hash(user_update.password)

    db.commit()
    db.refresh(user)

    return user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(database.get_db)
):
    """Delete current authenticated user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return None
