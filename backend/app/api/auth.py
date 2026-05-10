"""
User API routes - auth, profile, settings
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.database import get_db
from ..core.auth import hash_password, verify_password, create_access_token, decode_access_token
from ..models.database import User
from ..models.schemas import (
    UserRegister, UserLogin, UserUpdate, UserSettingsUpdate,
    UserResponse, LoginResponse, SuccessResponse
)

router = APIRouter(prefix="/auth", tags=["User Auth"])

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


# ========== Auth Endpoints ==========

@router.post("/register", response_model=LoginResponse)
async def register(request: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")

    # Create user
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        nickname=request.username,
        settings={
            "theme": "auto",
            "language": "zh",
            "temperature": 0.7,
            "send_with_enter": True
        }
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create token
    token = create_access_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=token,
        user=UserResponse(**user.to_dict())
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login"""
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    # Create token
    token = create_access_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=token,
        user=UserResponse(**user.to_dict())
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(**user.to_dict())


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    if request.nickname is not None:
        user.nickname = request.nickname
    if request.avatar is not None:
        user.avatar = request.avatar

    await db.commit()
    await db.refresh(user)

    return UserResponse(**user.to_dict())


@router.put("/settings", response_model=UserResponse)
async def update_settings(
    request: UserSettingsUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user settings"""
    if not user.settings:
        user.settings = {}

    update_data = request.model_dump(exclude_none=True)
    user.settings.update(update_data)

    await db.commit()
    await db.refresh(user)

    return UserResponse(**user.to_dict())


@router.put("/password", response_model=SuccessResponse)
async def change_password(
    old_password: str,
    new_password: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change password"""
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    user.hashed_password = hash_password(new_password)
    await db.commit()

    return SuccessResponse(message="Password changed successfully")
