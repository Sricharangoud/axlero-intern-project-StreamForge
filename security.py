from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from passlib.context import CryptContext
from app.core.config import settings

# CryptContext configured with bcrypt hashing algorithm for secure password storage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored bcrypt hash.
    
    :param plain_password: The user-entered raw password string.
    :param hashed_password: The salted bcrypt hash stored in the database.
    :return: True if password matches hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generates a secure salted bcrypt hash from a plain password.
    
    :param password: The plain-text password string to hash.
    :return: Salted bcrypt hash string.
    """
    return pwd_context.hash(password)


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Encodes a JSON Web Token (JWT) signed with the application SECRET_KEY.
    
    :param subject: Unique subject identifier (typically User ID or Email).
    :param expires_delta: Optional custom lifetime duration for the token.
    :return: Encoded JWT token string.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and validates an incoming JWT token string.
    
    :param token: The bearer token string from HTTP Authorization header.
    :return: Dictionary payload if valid, None if expired or tampered with.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        return None
