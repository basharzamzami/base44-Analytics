import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Create test database
SQLALCHEMY_DATABASE_URL = settings.database_test_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_tenant_and_user(setup_database):
    """Test tenant and user registration"""
    response = client.post("/api/v1/auth/register", json={
        "tenant": {
            "name": "Test Agency",
            "plan": "starter"
        },
        "user": {
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "owner"
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "tenant_id" in data
    assert "user_id" in data
    assert data["token_type"] == "bearer"

def test_login_user(setup_database):
    """Test user login"""
    # First register a user
    client.post("/api/v1/auth/register", json={
        "tenant": {
            "name": "Test Agency 2",
            "plan": "starter"
        },
        "user": {
            "email": "test2@example.com",
            "password": "testpassword123",
            "role": "owner"
        }
    })
    
    # Then login
    response = client.post("/api/v1/auth/login", data={
        "username": "test2@example.com",
        "password": "testpassword123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "tenant_id" in data
    assert "user_id" in data

def test_login_invalid_credentials(setup_database):
    """Test login with invalid credentials"""
    response = client.post("/api/v1/auth/login", data={
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_register_duplicate_email(setup_database):
    """Test registration with duplicate email"""
    # First registration
    client.post("/api/v1/auth/register", json={
        "tenant": {
            "name": "Test Agency 3",
            "plan": "starter"
        },
        "user": {
            "email": "duplicate@example.com",
            "password": "testpassword123",
            "role": "owner"
        }
    })
    
    # Second registration with same email
    response = client.post("/api/v1/auth/register", json={
        "tenant": {
            "name": "Test Agency 4",
            "plan": "starter"
        },
        "user": {
            "email": "duplicate@example.com",
            "password": "testpassword123",
            "role": "owner"
        }
    })
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

