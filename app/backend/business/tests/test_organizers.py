# tests/test_organizers.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from core.database import Base, get_db
from main import app
from models.models import Organizer

# ------------------- Configuración DB de test -------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_organizers.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------- Fixture DB -------------------
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)

# ------------------- Fixture TestClient -------------------
@pytest.fixture(scope="function")
def test_client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# ------------------- Fixture Organizer -------------------
@pytest.fixture(scope="function")
def create_test_organizer(db):
    organizer = Organizer(
        user_id=uuid4(),
        organization_name="Existing Org",
        status="draft"
    )
    db.add(organizer)
    db.commit()
    db.refresh(organizer)
    return organizer

# ------------------- Tests -------------------
def test_create_organizer(test_client):
    payload = {        
        "organization_name": "Test Org",
        "status": "draft"
    }

    fake_user_id = uuid4()

    response = test_client.post(
        "/organizers/",
        json=payload,
        headers={"Authorization": f"Bearer {fake_user_id}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["organization_name"] == payload["organization_name"]
    assert data["status"] == payload["status"]
    assert "id_organizer" in data

def test_get_organizer_by_id(test_client, create_test_organizer):
    response = test_client.get(f"/organizers/{create_test_organizer.id_organizer}")
    assert response.status_code == 200
    data = response.json()
    assert data["id_organizer"] == create_test_organizer.id_organizer
    assert data["organization_name"] == create_test_organizer.organization_name

def test_list_organizers(test_client, create_test_organizer):
    response = test_client.get("/organizers/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(o["id_organizer"] == create_test_organizer.id_organizer for o in data)

def test_update_organizer(test_client, create_test_organizer):
    payload = {"organization_name": "Updated Org", "status": "active"}
    response = test_client.put(f"/organizers/{create_test_organizer.id_organizer}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["organization_name"] == payload["organization_name"]
    assert data["status"] == payload["status"]

def test_delete_organizer(test_client, create_test_organizer):
    response = test_client.delete(f"/organizers/{create_test_organizer.id_organizer}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Organizer deleted succesfully"

    # Confirmar que ya no existe
    response_check = test_client.get(f"/organizers/{create_test_organizer.id_organizer}")
    assert response_check.status_code == 404
