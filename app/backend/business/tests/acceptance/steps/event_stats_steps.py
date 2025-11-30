import requests
from behave import given, when, then
from uuid import uuid4

BASE_URL = "http://localhost:8001"


# -----------------------------
#  Common step
# -----------------------------

# -----------------------------
#  Scenario step: setup full workflow
# -----------------------------
@given("an existing event with sales")
def step_create_event_with_sales(context):
    # 1. Crear organizador
    organizer_payload = {
        "user_id": str(uuid4()),
        "organization_name": "Test Org"
    }

    org_response = requests.post(f"{BASE_URL}/organizers/", json=organizer_payload)
    assert org_response.status_code == 200, \
        f"Organizer create failed: {org_response.status_code} {org_response.text}"

    organizer_id = org_response.json()["id_organizer"]
    creator_user_id = organizer_payload["user_id"]

    # Guardamos para después
    context.organizer_id = organizer_id
    context.creator_user_id = creator_user_id

    # 2. Crear evento
    event_payload = {
        "title": "Test Event",
        "description": "Event for statistics",
        "location": "Bogotá",
        "start_datetime": "2025-12-15T20:00:00",
        "price": 100.0,
        "capacity": 100,
        "status": "active",
        "organizer_id": organizer_id,
        "creator_user_id": creator_user_id,
    }

    event_response = requests.post(
        f"{BASE_URL}/events/",
        json=event_payload,
        headers={"Authorization": f"Bearer {creator_user_id}"}
    )
    assert event_response.status_code == 200, \
        f"Event creation failed: {event_response.status_code} {event_response.text}"

    event_id = event_response.json()["id_event"]
    context.event_id = event_id

    # 3. Crear orden para generar ventas
    order_payload = {
        "buyer_id": str(uuid4()),
        "buyer_name": "Test Buyer",
        "event_id": event_id,
        "quantity": 3
    }

    order_response = requests.post(f"{BASE_URL}/orders/", json=order_payload)
    assert order_response.status_code == 201, \
        f"Order failed: {order_response.status_code} {order_response.text}"


# -----------------------------
#  Fetch statistics
# -----------------------------
@when("I fetch the statistics for the organizer")
def step_fetch_stats(context):
    response = requests.get(
        f"{BASE_URL}/creator/{context.creator_user_id}",
        headers={"Authorization": f"Bearer {context.creator_user_id}"}
    )
    context.response = response



@then("the response should include the event statistics")
def step_validate_stats(context):
    data = context.response.json()
    assert isinstance(data, list), "Expected a list of events"

    # Buscar el evento creado
    event = next((e for e in data if e["id_event"] == context.event_id), None)
    assert event, f"Event {context.event_id} not found"

    # Validar estadísticas
    assert "tickets_sold" in event, "tickets_sold missing"
    assert "remaining_capacity" in event, "remaining_capacity missing"
    assert "capacity" in event, "capacity missing"

    # Validar ventas (3 tickets)
    assert event["tickets_sold"] == 3, \
        f"Expected 3 tickets sold, got {event['tickets_sold']}"

    assert event["remaining_capacity"] == event["capacity"] - 3, \
        "remaining_capacity does not equal capacity - tickets_sold"
