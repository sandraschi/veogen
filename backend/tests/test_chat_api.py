from types import SimpleNamespace
from pathlib import Path
from importlib import import_module
import sys

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

app = import_module("app.main").app
chat_endpoints = import_module("app.api.api_v1.endpoints.chat")


@pytest.fixture
def client(monkeypatch):
    """Create a FastAPI test client with chat dependencies overridden."""

    # Simple in-memory conversation store to avoid hitting the real database.
    conversation_store = {}

    async def override_get_current_user():
        return SimpleNamespace(id="test-user", email="test@example.com", is_active=True)

    def override_get_db():
        class DummySession:
            pass

        dummy = DummySession()
        try:
            yield dummy
        finally:
            return

    async def fake_generate_persona_response(conversation, db_session, user_id):
        return {
            "message": "Test response",
            "persona": {
                "id": conversation["persona_id"],
                "name": conversation["persona"]["name"],
            },
            "generated_content": None,
            "timestamp": "2025-01-01T00:00:00Z",
        }

    async def fake_save_conversation(conversation, db_session, user_id):
        conversation_store[conversation["id"]] = conversation

    async def fake_load_conversation(conversation_id, db_session, user_id):
        return conversation_store.get(conversation_id)

    app.dependency_overrides[chat_endpoints.get_current_user] = (
        override_get_current_user
    )
    app.dependency_overrides[chat_endpoints.get_db] = override_get_db

    monkeypatch.setattr(
        chat_endpoints.persona_chat_service,
        "_generate_persona_response",
        fake_generate_persona_response,
    )
    monkeypatch.setattr(
        chat_endpoints.persona_chat_service,
        "_save_conversation_to_db",
        fake_save_conversation,
    )
    monkeypatch.setattr(
        chat_endpoints.persona_chat_service,
        "_load_conversation_from_db",
        fake_load_conversation,
    )

    client_instance = TestClient(app)
    try:
        yield client_instance
    finally:
        app.dependency_overrides.pop(chat_endpoints.get_current_user, None)
        app.dependency_overrides.pop(chat_endpoints.get_db, None)
        client_instance.close()


def test_chat_conversation_flow(client):
    start_payload = {
        "persona_id": "creative_assistant",
        "initial_message": "Hello there, can you help me?",
    }

    start_response = client.post("/api/v1/chat/start", json=start_payload)
    assert start_response.status_code == 200

    start_data = start_response.json()
    assert start_data["status"] == "active"
    assert start_data["response"]["message"] == "Test response"
    conversation_id = start_data["conversation_id"]
    assert conversation_id

    message_response = client.post(
        f"/api/v1/chat/{conversation_id}/message",
        json={"message": "Give me creative ideas"},
    )
    assert message_response.status_code == 200

    message_data = message_response.json()
    assert message_data["status"] == "success"
    assert message_data["response"]["message"] == "Test response"

    history_response = client.get(f"/api/v1/chat/{conversation_id}/history")
    assert history_response.status_code == 200

    history_data = history_response.json()
    assert history_data["conversation_id"] == conversation_id
    assert history_data["message_count"] == len(history_data["messages"])
    assert history_data["messages"][-1]["role"] == "assistant"
