import pytest
import pytest_asyncio
import asyncio
from typing import Generator, AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.user import User
from app.core.security import security

# Test database URL
# Using localhost because tests run on host machine, and docker-compose exposes port 5432
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def engine():
    # Note: We are using the same postgres instance as dev but a different DB 'test_db'
    # We need to ensure 'test_db' exists or use the default one and clean it up.
    # Typically, we might want to connect to 'postgres' db first to create 'test_db'.
    # For now, let's assume 'test_db' might not exist and use 'management_api' (the default) 
    # OR we can try to create it.
    # Given the user provided code uses 'test_db', let's stick to it but we might need a helper to create it.
    # However, 'create_async_engine' will fail if db doesn't exist.
    # Let's use a workaround: Connect to default DB, create test_db if not exists.
    
    # Actually, let's try to connect to the default DB first to ensure connectivity.
    # If the user explicitly put 'test_db', they might have created it.
    # But to be safe and robust, I'll modify this slightly to handle DB creation if I can,
    # OR just use the user's code and let it fail if DB is missing (and then I'll fix it).
    # The user asked me to use *their* code. I should use it as close as possible.
    
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    # Attempt to drop/create tables. 
    # If database "test_db" does not exist, this line will raise an error.
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        # If connection fails (e.g. db doesn't exist), we might need to create it.
        # But for now, let's just proceed with the user's code structure.
        # I'll add a comment here about potential issues.
        raise

    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()
        await session.close()

@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator:
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Fixed extra spaces in URL from user input
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=security.get_password_hash("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """Get authentication headers for test user"""
    access_token = security.create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}
