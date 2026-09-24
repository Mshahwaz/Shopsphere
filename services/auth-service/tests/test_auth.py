from fastapi.testclient import TestClient
from sqlalchemy import select
from app.models import AuthUser
from app.security import verify_password
from app.database import SessionLocal
from app.main import app

client=TestClient(app)

def test_register_user():
    response=client.post(
        "/api/v1/auth/register",
        json={
            "email":"testuser1@example.com",
            "password":"StrongPAss@123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "testuser1@example.com"
    assert data["role"] == "USER"
    assert data["is_active"] is  True

    assert "password" not in data
    assert "password_hash" not in data

def test_register_duplicate_email():
    payload = {
        "email": "duplicate1@example.com",
        "password": "StrongPassword123",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert second_response.status_code == 409

def test_register_invalid_email():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 422

def test_register_short_password():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "short@example.com",
            "password": "123",
        },
    )

    assert response.status_code == 422

def test_password_is_hashed():
    password = "StrongPassword123"

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "hash@example.com",
            "password": password,
        },
    )

    assert response.status_code == 201

    with SessionLocal() as db:
        user = db.scalar(
            select(AuthUser).where(
                AuthUser.email == "hash@example.com"
            )
        )

        assert user is not None
        assert user.password_hash != password

        assert verify_password(
            password,
            user.password_hash,
        )