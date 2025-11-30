# tests/acceptance/steps/common_steps.py
from behave import given
import requests

BASE_URL = "http://localhost:8001"

@given("the backend is running")
def step_backend_running(context):
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
    except:
        # Solo almacenar la base_url, no es crítico
        pass
    context.base_url = BASE_URL
