import requests
from behave import given, when, then
from uuid import uuid4

BASE_URL = "http://localhost:8001"

# ---------------------
#   ESCENARIO 1
# ---------------------

@given('an existing order with id "1"')
def step_impl(context):
    """
    Creamos un order REAL porque tu backend no tiene uno por defecto.
    """
    # Crear organizer
    organizer_payload = {
        "user_id": str(uuid4()),
        "organization_name": "Test Org"
    }
    org_resp = requests.post(f"{BASE_URL}/organizers/", json=organizer_payload)
    assert org_resp.status_code in (200, 201)
    organizer_id = org_resp.json()["id_organizer"]

    # Crear event
    event_payload = {
        "title": "Test Event",
        "description": "Evento de prueba",
        "location": "Bogotá",
        "start_datetime": "2025-12-15T20:00:00",
        "price": 100.0,
        "capacity": 500,
        "status": "active",
        "organizer_id": organizer_id,
        "creator_user_id": organizer_payload["user_id"]
    }
    event_resp = requests.post(f"{BASE_URL}/events/", json=event_payload)
    assert event_resp.status_code in (200, 201)
    event_id = event_resp.json()["id_event"]

    # Crear order (este será id = 1 si tu DB está vacía)
    order_payload = {
        "buyer_id": str(uuid4()),
        "buyer_name": "Test Buyer",
        "event_id": event_id,
        "quantity": 1
    }
    order_resp = requests.post(f"{BASE_URL}/orders/", json=order_payload)
    assert order_resp.status_code in (200, 201)

    context.order_id = order_resp.json()["id_order"]


@when("I create a new payment with valid data")
def step_impl(context):
    payload = {
        "order_id": context.order_id,
        "provider_txn_id": str(uuid4()),
        "amount": 150.0
    }

    response = requests.post(BASE_URL + "/payments/", json=payload)

    context.response = response
    if response.status_code == 201:
        context.payment_id = response.json()["id_payment"]


@then("I should receive a 201 status code")
def step_impl(context):
    assert context.response.status_code == 201, \
        f"Expected 201, got {context.response.status_code}: {context.response.text}"


@then('the payment status should be "initiated"')
def step_impl(context):
    assert context.response.json()["status"] == "initiated", \
        f"Expected initiated, got {context.response.json()['status']}"


# ---------------------
#   ESCENARIO 2
# ---------------------

@given("an existing payment")
def step_impl(context):
    """
    Creamos toda la cadena completa: organizer → event → order → payment.
    """

    # Organizer
    organizer_payload = {
        "user_id": str(uuid4()),
        "organization_name": "Test Org 2"
    }
    org_resp = requests.post(f"{BASE_URL}/organizers/", json=organizer_payload)
    assert org_resp.status_code in (200, 201)
    organizer_id = org_resp.json()["id_organizer"]

    # Event
    event_payload = {
        "title": "Event Test 2",
        "description": "Evento para test",
        "location": "Medellín",
        "start_datetime": "2026-01-01T20:00:00",
        "price": 80.0,
        "capacity": 200,
        "status": "active",
        "organizer_id": organizer_id,
        "creator_user_id": organizer_payload["user_id"]
    }
    event_resp = requests.post(f"{BASE_URL}/events/", json=event_payload)
    assert event_resp.status_code in (200, 201)
    event_id = event_resp.json()["id_event"]

    # Order
    order_payload = {
        "buyer_id": str(uuid4()),
        "buyer_name": "Buyer Test 2",
        "event_id": event_id,
        "quantity": 2
    }
    order_resp = requests.post(f"{BASE_URL}/orders/", json=order_payload)
    assert order_resp.status_code in (200, 201)
    order_id = order_resp.json()["id_order"]

    # Payment
    payment_payload = {
        "order_id": order_id,
        "provider_txn_id": str(uuid4()),
        "amount": 150.0
    }
    pay_resp = requests.post(f"{BASE_URL}/payments/", json=payment_payload)
    assert pay_resp.status_code == 201

    context.payment_id = pay_resp.json()["id_payment"]


@when('I update the payment status to "completed"')
def step_impl(context):
    response = requests.put(
        f"{BASE_URL}/payments/{context.payment_id}/status",
        json={"status": "completed"}
    )
    context.update_response = response


@then('the payment status should be "completed"')
def step_impl(context):
    assert context.update_response.json()["status"] == "completed"
