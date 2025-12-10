from importlib import import_module
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

app = import_module("app.main").app
image_endpoints = import_module("app.api.api_v1.endpoints.image")


@pytest.fixture
def client(monkeypatch):
    async def override_get_current_user():
        return SimpleNamespace(id="test-user", email="test@example.com", is_active=True)

    app.dependency_overrides[image_endpoints.get_current_user] = override_get_current_user

    async def fake_generate_image(*_, **__):
        return {
            "status": "success",
            "message": "Test image generated",
            "image_data": b"fake-image-bytes",
            "api_used": "gemini_cli_mcp",
        }

    monkeypatch.setattr(
        image_endpoints.gemini_service,
        "generate_image",
        fake_generate_image,
    )

    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.pop(image_endpoints.get_current_user, None)
        test_client.close()


def test_generate_image_success(client):
    response = client.post(
        "/api/v1/image/generate",
        json={
            "prompt": "A scenic landscape with mountains",
            "aspect_ratio": "16:9",
            "style": "realistic",
            "num_images": 1,
            "creativity": 0.3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["api_used"] == "gemini_cli_mcp"
    assert len(payload["images"]) == 1
    assert payload["images"][0]["url"].startswith("data:image/png;base64,")
    metadata = payload["images"][0]["metadata"]
    assert metadata["prompt"] == "A scenic landscape with mountains"
    assert metadata["resolution"] == "1344x768"


def test_generate_image_propagates_errors(client, monkeypatch):
    async def failing_generate_image(*_, **__):
        return {"status": "error", "message": "upstream failure"}

    monkeypatch.setattr(
        image_endpoints.gemini_service,
        "generate_image",
        failing_generate_image,
    )

    response = client.post(
        "/api/v1/image/generate",
        json={"prompt": "Failure case"},
    )

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert "upstream failure" in detail

