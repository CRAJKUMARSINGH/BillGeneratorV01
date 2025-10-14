# tests/test_api_gateway.py
from fastapi.testclient import TestClient
from api.gateway import app

client = TestClient(app)

def test_generate_no_entrypoint():
    # If compute entrypoint not present, endpoint returns an informative error
    r = client.post("/generate", json={"input_data": {"hello":"world"}})
    assert r.status_code == 200
    assert "message" in r.json() or "status" in r.json()