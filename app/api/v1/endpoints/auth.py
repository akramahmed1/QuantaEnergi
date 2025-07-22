from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import get_db
from app.db.models import User
from app.db.schemas import UserCreate, Token
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await db.execute("SELECT * FROM users WHERE username = :username", {"username": form_data.username})
    user = user.first()
    if not user or not bcrypt.checkpw(form_data.password.encode(), user.hashed_password.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": "dummy-jwt-token", "token_type": "bearer"}

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    await db.execute("INSERT INTO users (username, email, hashed_password, role, is_active) VALUES (:username, :email, :hashed_password, :role, true)", 
                    {"username": user.username, "email": user.email, "hashed_password": hashed_password, "role": user.role})
    await db.commit()
    return {"msg": "User created"}