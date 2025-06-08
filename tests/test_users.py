from fastapi.testclient import TestClient
from sqlalchemy.orm import Session # For type hinting if using db_session fixture
import uuid # For unique usernames/emails

from core.config import settings

def test_user_registration(client: TestClient):
    unique_username = f"testuser_{uuid.uuid4().hex[:6]}"
    unique_email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    response = client.post(
        f"{settings.API_V1_STR}/users/register",
        json={"username": unique_username, "email": unique_email, "password": "testpassword123"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == unique_email
    assert "id" in data
    assert "password_hash" not in data # Ensure password hash isn't returned

def test_user_login(client: TestClient):
    # First, register a user to ensure they exist for login
    username = f"loginuser_{uuid.uuid4().hex[:6]}"
    email = f"login_{uuid.uuid4().hex[:6]}@example.com"
    password = "loginpassword123"
    reg_response = client.post(
        f"{settings.API_V1_STR}/users/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg_response.status_code == 201, f"Registration failed: {reg_response.text}"

    response = client.post(
        f"{settings.API_V1_STR}/users/login",
        data={"username": username, "password": password}, # Login uses form data
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_users_me_unauthenticated(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 401, response.text # Expect unauthorized

def test_get_users_me_authenticated(client: TestClient):
    # Register and login user
    username = f"me_user_{uuid.uuid4().hex[:6]}"
    email = f"me_{uuid.uuid4().hex[:6]}@example.com"
    password = "mepassword123"
    reg_response = client.post(
        f"{settings.API_V1_STR}/users/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg_response.status_code == 201, f"Registration failed: {reg_response.text}"

    login_response = client.post(
        f"{settings.API_V1_STR}/users/login", data={"username": username, "password": password}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email
