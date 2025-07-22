from datetime import datetime, timedelta
from jose import jwt
from app.core.config import config
from app.services.security import hash_password
import bcrypt
from oqs import KeyEncapsulation

def initialize_pqc_system():
    try:
        kem = KeyEncapsulation("Kyber1024")
        return kem
    except Exception as e:
        raise Exception(f"PQC initialization failed: {str(e)}")

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def get_password_hash(password: str) -> str:
    return hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))