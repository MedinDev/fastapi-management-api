import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_login_access_token(client: AsyncClient, db):
    # Create a user first
    # Since we are using the same DB as dev, this might conflict or leave data.
    # Ideally, we should use a factory or direct DB insertion, but for now we'll rely on the API flow or pre-existing user if available.
    # Or better, let's use the signup endpoint first.
    
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    
    # Try to signup first to ensure user exists
    signup_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    }
    
    # Check if user exists (we can't easily check DB directly without importing models and using session, which we can do via fixture)
    # But let's just try to signup, if 400, then user exists, we proceed to login.
    response = await client.post(f"{settings.API_V1_STR}/auth/signup", json=signup_data)
    if response.status_code != 201 and response.status_code != 400:
        # Unexpected error
        assert False, f"Signup failed with {response.status_code}: {response.text}"
        
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login", 
        data={"username": login_data["username"], "password": login_data["password"]},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_read_users_me(client: AsyncClient):
    # Signup and login to get token
    email = "me@example.com"
    password = "password123"
    
    await client.post(f"{settings.API_V1_STR}/auth/signup", json={
        "email": email,
        "username": "meuser",
        "password": password,
        "full_name": "Me User"
    })
    
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    token = login_res.json()["access_token"]
    
    response = await client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
