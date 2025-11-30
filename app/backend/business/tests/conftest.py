import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from core.database import Base, get_db
from models.models import Organizer
from uuid import uuid4
import jwt

# --------------------------
# BASE DE DATOS TEMPORAL
# --------------------------

@pytest.fixture(scope="session")
def db_file():
    """Archivo SQLite temporal en disco para toda la sesión de tests."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path

@pytest.fixture(scope="session")
def db_engine(db_file):
    """Motor de SQLAlchemy apuntando a la DB temporal."""
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False}
    )
    # Crear todas las tablas al inicio
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()
    os.remove(db_file)

    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Sesión SQLAlchemy aislada por test con rollback."""
    connection = db_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

# --------------------------
# CLIENTE DE FASTAPI
# --------------------------

@pytest.fixture(scope="function")
def test_client(db_session):
    """TestClient de FastAPI con DB de prueba."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# --------------------------
# FIXTURES DE DATOS DE PRUEBA
# --------------------------

@pytest.fixture
def create_test_organizer(db_session):
    """Crea un organizador de prueba."""
    organizer = Organizer(
        user_id=uuid4(),
        organization_name="Test Org"
    )
    db_session.add(organizer)
    db_session.commit()
    db_session.refresh(organizer)
    return organizer

@pytest.fixture
def create_fake_token():
    """Genera un token JWT de prueba."""
    def _create_fake_token(user_id, role="organizer"):
        payload = {
            "sub": str(user_id),
            "user_metadata": {"role": role}
        }
        return jwt.encode(payload, "test", algorithm="HS256")
    return _create_fake_token
