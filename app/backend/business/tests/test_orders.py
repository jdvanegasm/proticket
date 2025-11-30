import pytest
from uuid import uuid4

# IMPORTANTE: Usamos los fixtures de conftest.py
# test_client: TestClient de FastAPI
# db_session: sesión de SQLAlchemy con rollback
# create_test_organizer: organizador de prueba

# --------------------------
# FIXTURE AUXILIAR PARA CREAR EVENTOS
# --------------------------
@pytest.fixture
def create_test_event(test_client, create_test_organizer, create_fake_token):
    """Crea un evento de prueba y retorna su ID"""
    fake_token = create_fake_token(create_test_organizer.user_id)
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
    resp = test_client.post(
        "/events/",
        json=event_data,
        headers={"Authorization": f"Bearer {fake_token}"}
    )
    print(resp.json())  # Para depurar y ver si devuelve id_event
    assert resp.status_code == 200
    return resp.json()["id_event"]


# --------------------------
# TESTS
# --------------------------

def test_create_order(test_client, create_test_event):
    event_id = create_test_event

    order_data = {
        "buyer_id": str(uuid4()),
        "buyer_name": "Test Buyer",
        "event_id": event_id,
        "quantity": 2,                
    }

    resp = test_client.post("/orders/", json=order_data)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["event_id"] == event_id
    assert data["quantity"] == 2
    assert data["status"] == "pending"
    assert "id_order" in data


def test_get_order_by_id(test_client, create_test_event):
    event_id = create_test_event

    # Crear una orden primero
    order_data = {
        "buyer_id": str(uuid4()),
        "event_id": event_id,
        "buyer_name": "Test Buyer",
        "quantity": 1,                
    }
    create_resp = test_client.post("/orders/", json=order_data)
    data = create_resp.json()
    print(data)
    order_id = data["id_order"]
    
    resp = test_client.get(f"/orders/{order_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id_order"] == order_id
    assert "status" in data


def test_get_order_not_found(test_client):
    resp = test_client.get("/orders/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Orden not found"


def test_get_orders_by_user(test_client, create_test_event):
    event_id = create_test_event
    buyer_id = str(uuid4())

    # Crear una orden para el buyer
    order_data = {
        "event_id": event_id,
        "buyer_name": "Test Buyer",
        "quantity": 1,   
        "buyer_id": buyer_id
    }
    test_client.post("/orders/", json=order_data)

    resp = test_client.get(f"/orders/user/{buyer_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["buyer_id"] == buyer_id


from uuid import uuid4

def test_get_orders_by_user_not_found(test_client):
    buyer_id = str(uuid4())
    resp = test_client.get(f"/orders/user/{buyer_id}")
    assert resp.status_code == 200  
    data = resp.json()
    assert isinstance(data, list)     
    assert len(data) == 0           



def test_update_order_status(test_client, create_test_event):
    event_id = create_test_event

    # Crear orden
    order_data = {
        "event_id": event_id,
        "quantity": 1,
        "buyer_id": str(uuid4()),
        "buyer_name": "Test Buyer"
    }
    create_resp = test_client.post("/orders/", json=order_data)
    order_id = create_resp.json()["id_order"]

    update_data = {"status": "paid"}
    resp = test_client.put(f"/orders/{order_id}/status", json=update_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "paid"


def test_update_order_status_invalid(test_client, create_test_event):
    event_id = create_test_event

    # Crear orden
    order_data = {
        "event_id": event_id,
        "quantity": 1,
        "buyer_id": str(uuid4()),
        "buyer_name": "Test Buyer"
    }
    create_resp = test_client.post("/orders/", json=order_data)
    order_id = create_resp.json()["id_order"]

    # Intentar actualizar con un status inválido
    update_data = {"status": "invalid_status"}
    resp = test_client.put(f"/orders/{order_id}/status", json=update_data)
    assert resp.status_code == 400
