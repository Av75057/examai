from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.schemas import UserCreate, UserLogin, TokenResponse, UserProfile
from app.services.auth import create_user, authenticate_user, create_token, decode_token, get_user_by_id
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


async def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await create_user(db, data.email, data.password, data.name, data.grade)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    token = create_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.id)
    return TokenResponse(access_token=token)


class UserUpdate(BaseModel):
    grade: int | None = None
    name: str | None = None


@router.patch("/me", response_model=UserProfile)
async def update_profile(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_user),
):
    if data.grade is not None:
        if data.grade < 5 or data.grade > 11:
            raise HTTPException(status_code=400, detail="Класс должен быть от 5 до 11")
        user.grade = data.grade
    if data.name is not None:
        user.name = data.name
    await db.commit()
    return UserProfile(
        id=user.id,
        email=user.email,
        name=user.name,
        subscription=user.subscription.value if user.subscription else "free",
        grade=user.grade or 11,
    )


@router.get("/me", response_model=UserProfile)
async def me(user=Depends(current_user)):
    return UserProfile(
        id=user.id,
        email=user.email,
        name=user.name,
        subscription=user.subscription.value if user.subscription else "free",
        grade=user.grade or 11,
    )
