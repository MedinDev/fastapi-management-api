from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import security
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.email_service = EmailService()
    
    async def register_user(self, user_in: UserCreate) -> User:
        """Register a new user"""
        # Check if user exists
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Create new user
        # Note: In the user's provided code, they create a User object manually.
        # However, they pass hashed_password.
        # The user provided code uses security.get_password_hash(user_in.password).
        
        user = User(
            email=user_in.email,
            username=user_in.username,
            full_name=user_in.full_name,
            hashed_password=security.get_password_hash(user_in.password),
            role=user_in.role
        )
        
        created_user = await self.user_repo.create(user)
        
        # Send welcome email
        await self.email_service.send_welcome_email(created_user.email)
        
        return created_user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return user
    
    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        user = await self.user_repo.get_by_id(user_id)
        if user:
            # Replaced datetime.utcnow() with timezone-aware alternative as per best practices
            # But user provided datetime.utcnow(). I will use datetime.now(timezone.utc) to be safe and consistent with my previous fixes.
            user.last_login = datetime.now(timezone.utc)
            await self.db.commit()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repo.get_by_id(user_id)
