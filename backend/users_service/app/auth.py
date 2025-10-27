from passlib.context import CryptContext
from sqlalchemy.orm import Session
from . import models

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str) -> models.User | None:
    """
    Authenticate a user with username and password

    Args:
        db: Database session
        username: Username
        password: Plain text password

    Returns:
        User model if authentication successful, None otherwise
    """
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
