from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..db.session import get_db
from ..schemas.user import User
from ..core.security import get_password_hash, verify_password, create_access_token
from ..core.config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

# Pydantic models for request/response
class UserSignup(BaseModel):
    email: str
    password: str
    company_name: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    role: str
    company_name: str

@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        company_name=user_data.company_name,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        role=new_user.role,
        company_name=new_user.company_name
    )

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role,
        company_name=user.company_name
    )

@router.get("/me")
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user information."""
    from ..core.security import verify_token
    
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "company_name": user.company_name,
        "role": user.role,
        "subscription_plan": user.subscription_plan,
        "is_active": user.is_active,
        "created_at": user.created_at
    }
