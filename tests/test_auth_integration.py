import pytest
from httpx import AsyncClient
from app.models.user import User

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db_session):
    """Test user registration"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "SecurePass123!",
            "role": "user"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data
    assert "hashed_password" not in data

@pytest.mark.asyncio
async def test_register_cannot_self_assign_admin(client: AsyncClient):
    """Registration ignores a requested role and always creates a regular user"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "sneaky@example.com",
            "username": "sneaky",
            "full_name": "Sneaky User",
            "password": "SecurePass123!",
            "role": "admin"
        }
    )
    assert response.status_code == 200
    assert response.json()["role"] == "user"

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user: User):
    """Test login with invalid password"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers: dict):
    """Test getting current user info"""
    response = await client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers: dict):
    """Test logout functionality"""
    response = await client.post(
        "/api/v1/auth/logout",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"

    # The revoked token must no longer be accepted
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 401
