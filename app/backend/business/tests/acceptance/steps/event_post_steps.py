from behave import given, when, then
import requests
from uuid import uuid4

BASE_URL = "http://localhost:8001"

# ---------------------------
# GIVEN
# ---------------------------

@given("an existing organizer with credentials")
def step_existing_organizer(context):

    # Generamos un user_id REAL que será también el token
    user_id = str(uuid4())
    context.user_id = user_id
    context.token = f"Bearer {user_id}"

    context.organizer_payload = {
        "user_id": user_id,
        "organization_name": "Test Org"
    }

    response = requests.post(
        f"{BASE_URL}/organizers/",
        headers={"Authorization": context.token},
        json=context.organizer_payload
    )

    assert response.status_code == 200, f"Organizer creation failed: {response.text}"

    data = response.json()
    context.organizer_id = data["id_organizer"]


# ---------------------------
# WHEN
# ---------------------------

@when("I create a new event with valid data")
def step_create_event(context):
    print("Organizer ID used:", context.organizer_id)

    context.event_payload = {
        "title": "Rock Concert",
        "description": "A large outdoor concert",
        "location": "Main Stadium",
        "capacity": 5000,
        "price": 150.00,
        "start_datetime": "2025-12-25T20:00:00",
        "organizer_id": context.organizer_id
    }

    response = requests.post(
        f"{BASE_URL}/events/",
        headers={"Authorization": context.token},
        json=context.event_payload
    )

    context.response = response
    if response.status_code == 200:
        context.event_id = response.json().get("id_event")


@then("the response should contain the event information")
def step_event_info(context):
    data = context.response.json()

    for field in ["title", "description", "location", "capacity", "price", "start_datetime"]:
        assert field in data, f"Field '{field}' missing in event response"

    assert data["title"] == context.event_payload["title"]
