import requests
from behave import given, when, then
import json

API_URL = "http://localhost:8001/events"


@given("the system contains upcoming events")
def step_given_system_has_events(context):
    """
    No implementation required yet for acceptance testing.
    We assume the database already has events or will be mocked later.
    """
    pass


@when("the buyer requests the list of events")
def step_when_buyer_requests_events(context):
    context.response = requests.get(API_URL)


@then("the response should contain a list of events")
def step_then_list_of_events(context):
    data = context.response.json()
    assert isinstance(data, list), "Expected a list of events"
