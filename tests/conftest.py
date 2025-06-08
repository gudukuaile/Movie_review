from passlib.context import CryptContext
pwd_context_for_test = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password: str) -> str:
    return pwd_context_for_test.hash(password)
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import sys
import os

# Add project root to sys.path to allow importing 'main'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app # Main FastAPI application
from core.config import settings
from extend.database import Base, get_db # get_db dependency
from models import user_models, role_models # To create roles/users for testing
# For get_password_hash, ideally it's imported, but here it's injected.

# Use a separate test database (e.g., SQLite in-memory)
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency for tests
def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the override for the app instance used by TestClient
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create tables for the test session
    Base.metadata.create_all(bind=engine)

    # Seed initial data like roles
    db = TestingSessionLocal()
    try:
        role_models.Role.insert_roles(db_session=db)

        # Create a test admin user if needed for some tests
        admin_email = "testadmin@example.com"
        test_admin = db.query(user_models.User).filter(user_models.User.email == admin_email).first()
        if not test_admin:
            # get_password_hash is prepended to this file by the script
            hashed_password = get_password_hash("testadminpass")
            admin_role = db.query(role_models.Role).filter(role_models.Role.name == "Admin").first()
            if not admin_role: # Ensure admin role exists from insert_roles
                # This case should ideally not happen if insert_roles is robust
                print("Warning: Admin role not found during test admin creation. Attempting to create.")
                admin_role = role_models.Role(name="Admin", permissions=0xFFFF) # Example, adjust permissions
                db.add(admin_role)
                db.commit() # Commit the new role
                db.refresh(admin_role)

            test_admin = user_models.User(
                username="testadmin",
                email=admin_email,
                password_hash=hashed_password,
                role=admin_role
                # is_active=True was removed by script
            )
            db.add(test_admin)
            db.commit()
    finally:
        db.close()

    yield # Test session runs

    # Teardown: drop all tables after test session
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client() -> TestClient:
    # TestClient uses the app with the overridden get_db
    return TestClient(app)

@pytest.fixture(scope="module")
def db_session() -> Session:
    # A direct session fixture if needed for some setup/assertions outside TestClient
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
