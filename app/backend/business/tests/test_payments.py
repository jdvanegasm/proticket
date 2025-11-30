# backend/business/tests/test_payments.py
import pytest
from uuid import uuid4

# --------------------------
# FIXTURE AUXILIAR: Crear evento y orden de prueba
# --------------------------
@pytest.fixture
def create_test_order(test_client, create_test_organizer, create_fake_token):
    """
    Crea un evento de prueba y una orden asociada, retorna el ID de la orden.
    """
    # Generar token del organizador
    fake_token = create_fake_token(create_test_organizer.user_id)

    # Crear evento primero
    event_data = {
        "title": "Test Event",
        "description": "Evento para testing",
        "location": "Bogotá",
        "start_datetime": "2025-12-15T20:00:00",
        "price": 100.0,
        "capacity": 500,
        "status": "active",
        "organizer_id": create_test_organizer.id_organizer,
        "creator_user_id": str(create_test_organizer.user_id)
    }
    event_resp = test_client.post(
        "/events/",
        json=event_data,
        headers={"Authorization": f"Bearer {fake_token}"}
    )
    assert event_resp.status_code == 200
    event_id = event_resp.json()["id_event"]

    # Crear orden asociada al evento
    order_data = {
        "event_id": event_id,
        "buyer_id": str(uuid4()),
        "buyer_name": "Test Buyer",
        "quantity": 1
    }
    order_resp = test_client.post("/orders/", json=order_data)
    assert order_resp.status_code == 201

    return order_resp.json()["id_order"]

# --------------------------
# TESTS
# --------------------------

def test_create_payment(test_client, create_test_order):
    txn_id = str(uuid4())
    payment_data = {
        "id_payment": str(uuid4()),
        "order_id": create_test_order,
        "provider_txn_id": txn_id,
        "amount": "100.00"
    }

    response = test_client.post("/payments/", json=payment_data)
    assert response.status_code == 201

    data = response.json()
    assert data["order_id"] == create_test_order
    assert data["provider_txn_id"] == txn_id
    assert data["status"] == "initiated"
    assert str(data["amount"]) == "100.00"
    assert "id_payment" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_payment_by_id(test_client, create_test_order):
    txn_id = str(uuid4())
    payment_data = {
        "order_id": create_test_order,
        "provider_txn_id": txn_id,
        "amount": "50.00"
    }
    resp = test_client.post("/payments/", json=payment_data)
    payment_id = resp.json()["id_payment"]

    response = test_client.get(f"/payments/{payment_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id_payment"] == payment_id
    assert data["provider_txn_id"] == txn_id

def test_update_payment_status_valid(test_client, create_test_order):
    txn_id = str(uuid4())
    payment_data = {
        "order_id": create_test_order,
        "provider_txn_id": txn_id,
        "amount": "75.00"
    }
    resp = test_client.post("/payments/", json=payment_data)
    payment_id = resp.json()["id_payment"]

    update_data = {"status": "completed"}
    response = test_client.put(f"/payments/{payment_id}/status", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "completed"

def test_update_payment_status_invalid(test_client, create_test_order):
    txn_id = str(uuid4())
    payment_data = {
        "order_id": create_test_order,
        "provider_txn_id": txn_id,
        "amount": "30.00"
    }
    resp = test_client.post("/payments/", json=payment_data)
    payment_id = resp.json()["id_payment"]

    update_data = {"status": "invalid_status"}
    response = test_client.put(f"/payments/{payment_id}/status", json=update_data)
    assert response.status_code == 400
    assert "Invalid status" in response.json()["detail"]

def test_get_payment_not_found(test_client):
    fake_id = str(uuid4())
    response = test_client.get(f"/payments/{fake_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"
