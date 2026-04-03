"""Authentication service with password hashing and JWT token generation."""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import os
from pydantic import BaseModel

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
    """Hash a password using bcrypt directly.
    
    bcrypt has a 72-byte limit on passwords. If password exceeds this,
    it will be truncated before hashing.
    """
    # Input validation
    if password is None:
        raise ValueError("Password cannot be None")
    
    # Ensure password is a string and clean it
    password_str = str(password).strip()
    
    if not password_str:
        raise ValueError("Password cannot be empty")
    
    # Get the byte representation
    password_bytes = password_str.encode('utf-8')
    
    # **CRITICAL**: Truncate to 72 bytes BEFORE hashing
    # bcrypt WILL fail on anything longer
    if len(password_bytes) > 72:
        print(f"[WARN] Password is {len(password_bytes)} bytes, truncating to 72 for bcrypt")
        # Truncate UTF-8 bytes safely, handling multi-byte characters
        password_bytes = password_bytes[:72]
        # Decode back to string, ignoring incomplete multi-byte sequences
        password_str = password_bytes.decode('utf-8', errors='ignore')
    
    # Final validation before hash
    if len(password_str.encode('utf-8')) > 72:
        raise ValueError(f"Password still {len(password_str.encode('utf-8'))} bytes after truncation!")
    
    # Hash the password directly with bcrypt
    hashed = bcrypt.hashpw(password_str.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash using bcrypt directly.
    
    Apply the same truncation as hash_password for consistency.
    """
    password_str = str(plain_password).strip()
    # Get UTF-8 byte length and truncate if needed
    password_bytes = password_str.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate UTF-8 bytes and decode back to string
        password_bytes = password_bytes[:72]
        password_str = password_bytes.decode('utf-8', errors='ignore')
    
    # Verify directly with bcrypt
    try:
        return bcrypt.checkpw(password_str.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Bcrypt verification failed: {e}")
        return False


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
