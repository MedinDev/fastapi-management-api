import pytest
from httpx import AsyncClient
from app.main import app
from app.api import deps
from unittest.mock import AsyncMock, MagicMock
from app.core.config import settings

# Mock Redis
mock_redis = AsyncMock()
mock_redis.get.return_value = None
mock_redis.setex.return_value = True

async def override_get_redis():
    yield mock_redis

@pytest.mark.asyncio
async def test_auth_flow(client: AsyncClient):
    app.dependency_overrides[deps.get_redis] = override_get_redis
    # 1. Register
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    }
    response = await client.post(f"{settings.API_V1_STR}/auth/register", json=register_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == register_data["email"]
    assert "id" in data

    # 2. Login
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    response = await client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert response.status_code == 200, response.text
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    access_token = tokens["access_token"]

    # 3. Get Me
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
    assert response.status_code == 200, response.text
    user_data = response.json()
    assert user_data["email"] == register_data["email"]

    # 4. Logout
    response = await client.post(f"{settings.API_V1_STR}/auth/logout", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Successfully logged out"}
    
    # Verify Redis setex was called
    # mock_redis.setex.assert_called() # This might be tricky if setex is awaited. AsyncMock handles it.
    assert mock_redis.setex.called

