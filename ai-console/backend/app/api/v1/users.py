from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from jose import jwt

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.request.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserRequest,
    UserResponse,
    TokenResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.get("", response_model=dict)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    keyword: str = Query(None),
    status: str = Query(None),
    role: str = Query(None),
    role_id: int = Query(None),
    org_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.deleted_at.is_(None))

    if keyword:
        query = query.where(
            or_(
                User.username.ilike(f"%{keyword}%"),
                User.real_name.ilike(f"%{keyword}%"),
            )
        )
    if status:
        query = query.where(User.status == status)
    if role:
        query = query.where(User.role == role)
    if role_id:
        query = query.join(UserRole).where(UserRole.role_id == role_id)
    if org_id:
        query = query.where(User.org_id == org_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [UserResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{item_id}", response_model=UserResponse)
async def get_user(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.id == item_id, User.deleted_at.is_(None))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.post("/register", response_model=UserResponse)
async def register(data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == data.username, User.deleted_at.is_(None))
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = hash_password(data.password)
    user = User(
        username=data.username,
        password=hashed_password,
        real_name=data.real_name,
        email=data.email,
        phone=data.phone,
        gender=data.gender,
        org_id=data.org_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == data.username, User.deleted_at.is_(None))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return TokenResponse(access_token=access_token)


@router.post("", response_model=UserResponse)
async def create_user(data: UserRequest, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == data.username, User.deleted_at.is_(None))
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user_data = data.model_dump(exclude={"password"})
    if data.password:
        user_data["password"] = hash_password(data.password)

    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/{item_id}", response_model=UserResponse)
async def update_user(item_id: int, data: UserRequest, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.id == item_id, User.deleted_at.is_(None))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = data.model_dump(exclude={"password"})
    if data.password:
        user_data["password"] = hash_password(data.password)

    for key, value in user_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/{item_id}")
async def delete_user(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.id == item_id, User.deleted_at.is_(None))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "User deleted"}


@router.post("/{item_id}/reset-password")
async def reset_user_password(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.id == item_id, User.deleted_at.is_(None))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Reset to default password
    user.password = hash_password("123456")
    await db.commit()
    return {"message": "Password reset successfully"}