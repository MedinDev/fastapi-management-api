import asyncio
import sys
import os

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import security

async def create_initial_data() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
        )
        user = result.scalars().first()

        if not user:
            print(f"Creating superuser {settings.FIRST_SUPERUSER_EMAIL}")
            user = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                username="admin",
                full_name="Super Admin",
                hashed_password=security.get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                role=UserRole.ADMIN.value,
                is_active=True,
                is_verified=True,
                is_superuser=True,
            )
            session.add(user)
            await session.commit()
            print("Superuser created successfully")
        else:
            print(f"Superuser {settings.FIRST_SUPERUSER_EMAIL} already exists")

async def main() -> None:
    print("Seeding initial data...")
    await create_initial_data()
    print("Initial data seeded")

if __name__ == "__main__":
    asyncio.run(main())
