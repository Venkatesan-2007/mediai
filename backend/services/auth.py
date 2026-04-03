"""Authentication service with password hashing and JWT token generation."""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import os
from pydantic import BaseModel

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


class TokenData(BaseModel):
    """Token payload data."""
    user_id: int
    username: str
    exp: datetime


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    user: dict


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    bcrypt has a 72-byte limit on passwords. If password exceeds this,
    it will be truncated before hashing.
    """
    # Ensure password is a string and strip whitespace
    if not isinstance(password, str):
        password = str(password)
    
    password_str = password.strip()
    
    # Truncate to 72 bytes (bcrypt's maximum)
    # Important: we must truncate BEFORE passing to bcrypt
    if len(password_str.encode('utf-8')) > 72:
        # Truncate UTF-8 bytes safely
        password_bytes = password_str.encode('utf-8')[:72]
        # Decode, ignoring any incomplete multibyte characters at the boundary
        password_str = password_bytes.decode('utf-8', errors='ignore')
    
    # Hash the (possibly truncated) password
    try:
        hashed = pwd_context.hash(password_str)
        return hashed
    except ValueError as e:
        # If hashing still fails, truncate more aggressively
        if 'password_has_invalid_bytes' in str(e) or 'password' in str(e):
            password_str = password_str[:60]  # Extra safe truncation
            return pwd_context.hash(password_str)
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash.
    
    Apply the same truncation as hash_password for consistency.
    """
    password_str = str(plain_password).strip()
    # Get UTF-8 byte length and truncate if needed
    password_bytes = password_str.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate UTF-8 bytes and decode back to string
        password_bytes = password_bytes[:72]
        password_str = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(password_str, hashed_password)


def create_access_token(user_id: int, username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "user_id": user_id,
        "username": username,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        
        if user_id is None or username is None:
            return None
        
        return TokenData(
            user_id=user_id,
            username=username,
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
    except JWTError:
        return None
