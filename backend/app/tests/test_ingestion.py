import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.models.tenant import Tenant
from app.models.user import User
from app.models.connector import Connector, RawIngest
from app.core.security import get_password_hash

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

@pytest.fixture
def test_tenant_and_user(setup_database):
    """Create a test tenant and user"""
    db = TestingSessionLocal()
    
    # Create tenant
    tenant = Tenant(name="Test Agency", plan="starter")
    db.add(tenant)
    db.flush()
    
    # Create user
    user = User(
        tenant_id=tenant.id,
        email="test@example.com",
        role="owner",
        hashed_password=get_password_hash("testpassword123")
    )
    db.add(user)
    db.commit()
    db.refresh(tenant)
    db.refresh(user)
    
    yield tenant, user
    db.close()

@pytest.fixture
def auth_headers(test_tenant_and_user):
    """Get authentication headers for test user"""
    tenant, user = test_tenant_and_user
    
    # Login to get token
    response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword123"
    })
    
    token = response.json()["access_token"]
    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": str(tenant.id)
    }

def test_create_connector(auth_headers, test_tenant_and_user):
    """Test creating a connector"""
    tenant, user = test_tenant_and_user
    
    response = client.post("/api/v1/connectors/", 
        json={
            "type": "csv",
            "config_json": {"delimiter": ","}
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "csv"
    assert data["tenant_id"] == tenant.id
    assert "id" in data

def test_list_connectors(auth_headers, test_tenant_and_user):
    """Test listing connectors"""
    tenant, user = test_tenant_and_user
    
    # Create a connector first
    client.post("/api/v1/connectors/", 
        json={
            "type": "csv",
            "config_json": {"delimiter": ","}
        },
        headers=auth_headers
    )
    
    # List connectors
    response = client.get("/api/v1/connectors/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "csv"

def test_connector_sync(auth_headers, test_tenant_and_user):
    """Test connector sync"""
    tenant, user = test_tenant_and_user
    
    # Create a connector
    create_response = client.post("/api/v1/connectors/", 
        json={
            "type": "csv",
            "config_json": {"delimiter": ","}
        },
        headers=auth_headers
    )
    connector_id = create_response.json()["id"]
    
    # Sync the connector
    response = client.post(f"/api/v1/connectors/{connector_id}/sync", 
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "records_ingested" in data

def test_tenant_isolation(auth_headers, test_tenant_and_user):
    """Test that tenants cannot access each other's data"""
    tenant, user = test_tenant_and_user
    
    # Create another tenant and user
    db = TestingSessionLocal()
    other_tenant = Tenant(name="Other Agency", plan="starter")
    db.add(other_tenant)
    db.flush()
    
    other_user = User(
        tenant_id=other_tenant.id,
        email="other@example.com",
        role="owner",
        hashed_password=get_password_hash("testpassword123")
    )
    db.add(other_user)
    db.commit()
    db.close()
    
    # Try to access other tenant's data
    other_auth_headers = {
        "Authorization": auth_headers["Authorization"],  # Same token
        "X-Tenant-ID": str(other_tenant.id)  # But different tenant ID
    }
    
    response = client.get("/api/v1/connectors/", headers=other_auth_headers)
    assert response.status_code == 403
    assert "Access denied to this tenant" in response.json()["detail"]

def test_missing_tenant_header():
    """Test that requests without X-Tenant-ID header are rejected"""
    response = client.get("/api/v1/connectors/")
    assert response.status_code == 422  # Validation error for missing header

