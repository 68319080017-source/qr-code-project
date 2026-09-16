from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from app.core.config import settings
import hashlib

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using SHA-256 (portable fallback)."""
    return _hash_password(plain_password) == hashed_password

def get_password_hash(password: str) -> str:
    """Hash a password using SHA-256 (portable, no bcrypt dependency issues)."""
    return _hash_password(password)

def _hash_password(password: str) -> str:
    """Simple SHA-256 hash with salt from SECRET_KEY."""
    salted = f"{settings.SECRET_KEY}:{password}"
    return hashlib.sha256(salted.encode()).hexdigest()

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
