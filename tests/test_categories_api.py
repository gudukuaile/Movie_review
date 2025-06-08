from fastapi.testclient import TestClient
from sqlalchemy.orm import Session # For type hinting
import uuid

from core.config import settings
# from tests.conftest import engine as test_engine # Not needed directly usually
# from models import user_models, role_models # Not needed directly for these tests

def get_admin_auth_headers(client: TestClient) -> dict:
    login_data = {
        "username": "testadmin",
        "password": "testadminpass"
    }
    response = client.post(f"{settings.API_V1_STR}/users/login", data=login_data)
    if response.status_code != 200:
        print(f"Admin login failed in test setup. Status: {response.status_code}, Response: {response.text}")
        # Attempt to register the admin if login fails, could be first run against clean test DB part of a split session
        # This is a fallback, ideally conftest ensures admin exists.
        # However, conftest runs once per session, and client fixture might be per module.
        # For simplicity here, just raise error if initial login fails.
        raise Exception(f"Admin login failed during test setup. Status: {response.status_code}, Detail: {response.text}")

    tokens = response.json()
    a_token = tokens["access_token"]
    return {"Authorization": f"Bearer {a_token}"}


def test_create_category(client: TestClient):
    admin_headers = get_admin_auth_headers(client)
    category_name = f"Test Category {uuid.uuid4().hex[:6]}"
    response = client.post(
        f"{settings.API_V1_STR}/categories/",
        json={"name": category_name},
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == category_name
    assert "id" in data

def test_read_categories(client: TestClient):
    admin_headers = get_admin_auth_headers(client)
    # Create a category first to ensure list is not empty
    category_name = f"Test Read Cat {uuid.uuid4().hex[:6]}"
    create_resp = client.post(
        f"{settings.API_V1_STR}/categories/",
        json={"name": category_name},
        headers=admin_headers,
    )
    assert create_resp.status_code == 201, f"Failed to create category for reading test: {create_resp.text}"

    response = client.get(f"{settings.API_V1_STR}/categories/", headers=admin_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert any(item["name"] == category_name for item in data), f"Category {category_name} not found in list."
