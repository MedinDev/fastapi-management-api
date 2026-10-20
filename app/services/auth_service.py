from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional

from app.models.user import User, UserRole
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
        
        user = User(
            email=user_in.email,
            username=user_in.username,
            full_name=user_in.full_name,
            hashed_password=security.get_password_hash(user_in.password),
            # Self-registration always creates a regular user; roles are granted by an admin
            role=UserRole.USER
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
            user.last_login = datetime.now(timezone.utc)
            await self.db.commit()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repo.get_by_id(user_id)
