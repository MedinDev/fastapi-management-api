from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from typing import Any

from app.api import deps
from app.schemas.token import Token, RefreshToken
from app.schemas.user import User, UserCreate
from app.services.auth_service import AuthService
from app.core.security import security
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register", response_model=User)
async def register(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """Register a new user"""
    auth_service = AuthService(db)
    try:
        user = await auth_service.register_user(user_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return user

@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(
        email=form_data.username,
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    await auth_service.update_last_login(user.id)
    
    return {
        "access_token": security.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        ),
        "refresh_token": security.create_refresh_token(
            data={"sub": str(user.id)}
        ),
        "token_type": "bearer"
    }

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(
    *,
    token_data: RefreshToken,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """Refresh access token"""
    payload = security.verify_token(token_data.refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(int(payload["sub"]))
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return {
        "access_token": security.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        ),
        "refresh_token": security.create_refresh_token(
            data={"sub": str(user.id)}
        ),
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    redis_client = Depends(deps.get_redis)
) -> Any:
    """Logout user (blacklist token)"""
    # Add token to blacklist with expiry
    await redis_client.setex(f"blacklist:{token}", settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, 1)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get current user"""
    return current_user
