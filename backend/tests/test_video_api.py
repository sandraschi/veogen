from importlib import import_module
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

app = import_module("app.main").app
video_endpoints = import_module("app.api.api_v1.endpoints.video")


@pytest.fixture
def client(monkeypatch):
    async def override_get_current_user():
        return SimpleNamespace(id="test-user", email="test@example.com", is_active=True)

    app.dependency_overrides[video_endpoints.get_current_user] = override_get_current_user

    async def fake_generate_video(*_, **__):
        return {
            "status": "success",
            "message": "Test video generated",
            "video_data": b"fake-video-bytes",
            "duration": 8,
            "aspect_ratio": "16:9",
            "style": "cinematic",
            "api_used": "gemini_cli_mcp",
        }

    monkeypatch.setattr(
        video_endpoints.gemini_service,
        "generate_video",
        fake_generate_video,
    )

    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.pop(video_endpoints.get_current_user, None)
        test_client.close()


def test_generate_video_success(client):
    response = client.post(
        "/api/v1/video/generate",
        json={
            "prompt": "A sweeping drone shot over snowy mountains at sunrise",
            "duration": 12,
            "aspect_ratio": "16:9",
            "style": "cinematic",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["api_used"] == "gemini_cli_mcp"
    video = payload["video"]
    assert video["url"].startswith("data:video/mp4;base64,")
    assert video["metadata"]["style"] == "cinematic"


def test_generate_video_handles_errors(client, monkeypatch):
    async def failing_generate_video(*_, **__):
        return {"status": "error", "message": "veo model unavailable"}

    monkeypatch.setattr(
        video_endpoints.gemini_service,
        "generate_video",
        failing_generate_video,
    )

    response = client.post(
        "/api/v1/video/generate",
        json={"prompt": "Failure case"},
    )

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert "veo model unavailable" in detail

