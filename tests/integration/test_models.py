import pytest


def test_register_model_api(client, api_headers, valid_model_payload):
    response = client.post("/api/v1/models/register", json=valid_model_payload, headers=api_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == valid_model_payload["name"]
    assert data["version"] == valid_model_payload["version"]
    assert data["path"] == valid_model_payload["path"]
    assert data["metrics"] == valid_model_payload["metrics"]
    assert data["stage"] == valid_model_payload["stage"]
    assert data["id"] is not None
