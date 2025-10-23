from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..db.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")  # user, admin, trader, analyst
    subscription_plan = Column(String, default="basic")  # basic, pro, enterprise
    api_calls_this_month = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', company='{self.company_name}')>"

# Pydantic schemas for API operations
class UserBase(BaseModel):
    email: EmailStr
    company_name: str
    role: Optional[str] = "user"
    subscription_plan: Optional[str] = "basic"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    company_name: Optional[str] = None
    role: Optional[str] = None
    subscription_plan: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    api_calls_this_month: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
