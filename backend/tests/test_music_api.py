from importlib import import_module
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

app = import_module("app.main").app
music_endpoints = import_module("app.api.api_v1.endpoints.music")


@pytest.fixture
def client(monkeypatch):
    async def override_get_current_user():
        return SimpleNamespace(id="test-user", email="test@example.com", is_active=True)

    app.dependency_overrides[music_endpoints.get_current_user] = override_get_current_user

    async def fake_generate_music(*_, **__):
        return {
            "status": "success",
            "message": "Test music generated",
            "music_data": b"fake-music-bytes",
            "duration": 30,
            "style": "electronic",
            "api_used": "gemini_cli_mcp",
        }

    monkeypatch.setattr(
        music_endpoints.gemini_service,
        "generate_music",
        fake_generate_music,
    )

    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.pop(music_endpoints.get_current_user, None)
        test_client.close()


def test_generate_music_success(client):
    response = client.post(
        "/api/v1/music/generate",
        json={
            "prompt": "Calming piano melody for relaxation",
            "genre": "ambient",
            "duration": 45,
            "tempo": 80,
            "mood": "relaxing",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["api_used"] == "gemini_cli_mcp"
    track = payload["track"]
    assert track["url"].startswith("data:audio/mpeg;base64,")
    assert track["metadata"]["genre"] == "ambient"


def test_generate_music_handles_service_errors(client, monkeypatch):
    async def failing_generate_music(*_, **__):
        return {"status": "error", "message": "music model offline"}

    monkeypatch.setattr(
        music_endpoints.gemini_service,
        "generate_music",
        failing_generate_music,
    )

    response = client.post(
        "/api/v1/music/generate",
        json={"prompt": "Failure case"},
    )

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert "music model offline" in detail

