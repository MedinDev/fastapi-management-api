import pytest
from app.core.security import security
from app.schemas.user import UserCreate
from app.models.user import User, UserRole
from pydantic import ValidationError

def test_password_hashing():
    password = "secret_password"
    hashed = security.get_password_hash(password)
    assert security.verify_password(password, hashed)
    assert not security.verify_password("wrong_password", hashed)

def test_jwt_token():
    data = {"sub": "123"}
    token = security.create_access_token(data)
    payload = security.verify_token(token)
    assert payload is not None
    assert payload["sub"] == "123"
    assert payload["type"] == "access"

def test_user_schema_validation():
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
        full_name="Test User"
    )
    assert user_in.email == "test@example.com"

    with pytest.raises(ValidationError):
        UserCreate(
            email="invalid-email",
            username="test",
            password="pwd",
            full_name="Test"
        )

def test_user_model_instantiation():
    user = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        role=UserRole.ADMIN
    )
    assert user.role == UserRole.ADMIN
