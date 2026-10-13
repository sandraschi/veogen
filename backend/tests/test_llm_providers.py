"""Local + cloud LLM provider layer (offline: no network, temp data dir)."""

import asyncio
from importlib import import_module
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.services import llm_providers as llm

SECRET = "sk-test-SECRET-1234567890"


@pytest.fixture(autouse=True)
def tmp_data(tmp_path, monkeypatch):
    monkeypatch.setenv("VEOGEN_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    return tmp_path


def test_keystore_roundtrip_and_env_wins(monkeypatch):
    assert not llm.is_configured("openai")
    llm.save_key("openai", SECRET)
    assert llm.get_key("openai") == SECRET
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    assert llm.get_key("openai") == "env-key"
    monkeypatch.delenv("OPENAI_API_KEY")
    assert llm.delete_key("openai") is True
    assert not llm.is_configured("openai")


def test_local_providers_take_no_key():
    with pytest.raises(ValueError):
        llm.save_key("ollama", "x")
    assert llm.is_configured("ollama")


def test_public_info_never_contains_key():
    llm.save_key("openai", SECRET)
    assert SECRET not in repr(llm.public_provider_info())
    assert SECRET not in repr(llm.keys_configured())


def test_selection_default_and_persist():
    assert llm.get_selection() == llm.DEFAULT_SELECTION
    llm.save_selection("ollama", "gemma4:12b")
    assert llm.get_selection() == {"provider": "ollama", "model": "gemma4:12b"}
    with pytest.raises(ValueError):
        llm.save_selection("nope", "m")


def test_request_mapping():
    msgs = [{"role": "system", "content": "be brief"}, {"role": "user", "content": "hi"}]
    anth = llm._build_request(llm.require_provider("anthropic"), "claude-x", msgs, 0.3, 50, False)
    assert anth["system"] == "be brief" and anth["messages"] == [{"role": "user", "content": "hi"}]
    assert anth["max_tokens"] == 50 and anth["temperature"] == 0.3
    oll = llm._build_request(llm.require_provider("ollama"), "gemma", msgs, 0.5, 64, True)
    assert oll["options"] == {"num_ctx": llm.OLLAMA_NUM_CTX, "temperature": 0.5, "num_predict": 64}
    assert oll["stream"] is True
    oai = llm._build_request(llm.require_provider("google"), "gemini-3.8-flash", msgs, None, None, False)
    assert oai == {"model": "gemini-3.8-flash", "messages": msgs, "stream": False}


def test_google_model_ids_drop_models_prefix():
    payload = {"data": [{"id": "models/gemini-3.8-flash"}, {"id": "gemini-3.1-pro-preview"}]}
    assert llm._parse_model_list("openai", payload) == ["gemini-3.8-flash", "gemini-3.1-pro-preview"]


def test_complete_text_builds_messages_and_uses_selection(monkeypatch):
    llm.save_selection("ollama", "gemma4:12b")
    seen = {}

    async def fake_chat(provider, model, messages, temperature=None, max_tokens=None):
        seen.update(provider=provider, model=model, messages=messages, temperature=temperature)
        return "ok"

    monkeypatch.setattr(llm, "chat_complete", fake_chat)
    out = asyncio.run(
        llm.complete_text("next?", system="sys", history=[{"role": "user", "content": "a"}], temperature=0.2)
    )
    assert out == "ok"
    assert seen["provider"] == "ollama" and seen["model"] == "gemma4:12b"
    assert [m["role"] for m in seen["messages"]] == ["system", "user", "user"]
    assert seen["messages"][-1]["content"] == "next?"


def test_cloud_without_key_is_an_error(monkeypatch):
    monkeypatch.setattr(llm, "get_key", lambda _p: "")
    with pytest.raises(ValueError):
        asyncio.run(llm.chat_complete("openai", "gpt-4o", [{"role": "user", "content": "x"}]))


def test_facade_generate_content_is_awaitable(monkeypatch):
    from app.services.gemini_service import gemini_service

    async def fake_complete(prompt, **kwargs):
        return f"echo:{prompt}"

    monkeypatch.setattr(llm, "complete_text", fake_complete)
    assert asyncio.run(gemini_service.generate_content("hello")) == "echo:hello"


@pytest.fixture
def client(monkeypatch):
    app = import_module("app.main").app
    routes = import_module("app.api.llm_routes")

    async def fake_probe(_p):
        return False, []

    monkeypatch.setattr(llm, "probe_local", fake_probe)
    yield TestClient(app), app, routes
    app.dependency_overrides.clear()


def test_routes_shape_auth_and_no_key_leak(client):
    tc, app, routes = client
    rows = tc.get("/api/llm/providers").json()
    assert {r["id"] for r in rows} >= {"ollama", "google", "openai"}
    assert all("detected" in r for r in rows if r["kind"] == "local")

    assert tc.post("/api/settings/llm", json={"provider": "openai", "api_key": SECRET}).status_code in (401, 403)

    async def fake_user():
        return SimpleNamespace(id="u", email="u@example.com", is_active=True)

    app.dependency_overrides[routes.get_current_user] = fake_user
    resp = tc.post("/api/settings/llm", json={"provider": "openai", "model": "gpt-4o", "api_key": SECRET})
    assert resp.status_code == 200
    assert SECRET not in resp.text
    body = tc.get("/api/settings/llm").json()
    assert body["provider"] == "openai" and body["model"] == "gpt-4o" and body["api_key_configured"] is True
    assert SECRET not in tc.get("/api/settings/llm").text
    assert SECRET not in tc.get("/api/llm/providers").text
    assert tc.delete("/api/settings/llm/key", params={"provider": "openai"}).json()["removed"] is True
