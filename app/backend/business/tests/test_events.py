import pytest
from models.models import Organizer
from main import app
from uuid import uuid4

# Los fixtures db_session, test_client, create_test_organizer y create_fake_token
# se definen en conftest.py

# -----------------------------
# TESTS
# -----------------------------

def test_create_event(test_client, create_test_organizer, create_fake_token):
    fake_user_id = create_test_organizer.user_id
    fake_token = create_fake_token(fake_user_id)

    event_data = {
        "title": "Concierto de Prueba",
        "description": "Descripción del evento",
        "location": "Bogotá",
        "start_datetime": "2025-12-20T20:00:00",
        "price": 150.50,
        "capacity": 200,
        "status": "active",
        "organizer_id": create_test_organizer.id_organizer
    }

    response = test_client.post(
        "/events/",
        json=event_data,
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["creator_user_id"] == str(fake_user_id)
    assert data["organizer_id"] == create_test_organizer.id_organizer
    assert data["title"] == event_data["title"]


def test_get_all_events(test_client, create_test_organizer, create_fake_token):
    fake_token = create_fake_token(create_test_organizer.user_id)

    # Crear un evento para garantizar que haya al menos uno
    test_client.post(
        "/events/",
        json={
            "title": "Evento Lista",
            "description": "Evento para prueba de lista",
            "location": "Bogotá",
            "start_datetime": "2025-12-21T20:00:00",
            "price": 100.0,
            "capacity": 50,
            "status": "active",
            "organizer_id": create_test_organizer.id_organizer
        },
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    response = test_client.get("/events/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_event_by_id(test_client, create_test_organizer, create_fake_token):
    fake_token = create_fake_token(create_test_organizer.user_id)

    # Crear evento
    create_resp = test_client.post(
        "/events/",
        json={
            "title": "Evento Detalle",
            "description": "Detalle de evento",
            "location": "Bogotá",
            "start_datetime": "2025-12-22T20:00:00",
            "price": 120.0,
            "capacity": 80,
            "status": "active",
            "organizer_id": create_test_organizer.id_organizer
        },
        headers={"Authorization": f"Bearer {fake_token}"}
    )
    event_id = create_resp.json()["id_event"]

    response = test_client.get(f"/events/{event_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id_event"] == event_id
    assert data["title"] == "Evento Detalle"


def test_get_event_not_found(test_client, create_test_organizer, create_fake_token):
    fake_token = create_fake_token(create_test_organizer.user_id)

    response = test_client.get(
        "/events/999",
        headers={"Authorization": f"Bearer {fake_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Evento no encontrado"


def test_delete_event(test_client, create_test_organizer, create_fake_token):
    fake_token = create_fake_token(create_test_organizer.user_id)

    # Crear evento a borrar
    create_resp = test_client.post(
        "/events/",
        json={
            "title": "Evento a borrar",
            "description": "Este evento será eliminado",
            "location": "Bogotá",
            "start_datetime": "2025-12-23T20:00:00",
            "price": 90.0,
            "capacity": 30,
            "status": "active",
            "organizer_id": create_test_organizer.id_organizer
        },
        headers={"Authorization": f"Bearer {fake_token}"}
    )
    event_id = create_resp.json()["id_event"]

    del_resp = test_client.delete(
        f"/events/{event_id}",
        headers={"Authorization": f"Bearer {fake_token}"}
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "Evento eliminado exitosamente"


def test_delete_event_not_found(test_client, create_test_organizer, create_fake_token):
    fake_token = create_fake_token(create_test_organizer.user_id)

    response = test_client.delete(
        "/events/9999",
        headers={"Authorization": f"Bearer {fake_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Evento no encontrado"
