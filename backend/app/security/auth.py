import jwt
from datetime import datetime, timedelta
from typing import Optional

JWT_SECRET = "supersecret"
JWT_ALGORITHM = "HS256"

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    
    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return subject"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
