from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.db.models import User
from app.core.security import create_access_token, get_password_hash, verify_password

router = APIRouter()

@router.post("/register")
async def register_user(username: str, email: str, password: str, role: str, db: AsyncSession = Depends(AsyncSessionLocal)):
    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password, role=role, is_active=True)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"msg": "User registered"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(AsyncSessionLocal)):
    user = await db.execute(db.select(User).filter(User.email == form_data.username))
    user = user.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}