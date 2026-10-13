"""Movie production REST + MCP surfaces: cost guardrail, auth, planning (offline)."""

import asyncio
import json
import time
from importlib import import_module
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.services import llm_providers
from app.services import movie_pipeline as mp

SCRIPT = json.dumps({"synopsis": "s", "scenes": [{"title": "A", "visual_prompt": "a lighthouse at dusk"}]})
BODY = {"title": "Lighthouse", "concept": "A lonely lighthouse keeper finds a message in a bottle.", "scene_count": 1}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(mp.settings, "OUTPUT_DIR", str(tmp_path / "outputs"))
    monkeypatch.setenv("VEOGEN_DATA_DIR", str(tmp_path / "data"))

    async def fake_complete(prompt, **kwargs):
        return SCRIPT

    monkeypatch.setattr(llm_providers, "complete_text", fake_complete)

    def no_paid_calls():
        raise AssertionError("media client must not be created in these tests")

    monkeypatch.setattr(mp, "client_factory", no_paid_calls)
    app = import_module("app.main").app
    movie = import_module("app.api.api_v1.endpoints.movie")
    with TestClient(app) as tc:
        yield tc, app, movie
    app.dependency_overrides.clear()


def _login(app, movie):
    async def fake_user():
        return SimpleNamespace(id="u", email="u@example.com", is_active=True)

    app.dependency_overrides[movie.get_current_user] = fake_user


def test_estimate_route_is_free_and_priced(client):
    tc, _app, _movie = client
    est = tc.post("/api/v1/movie/productions/estimate", json={**BODY, "scene_count": 4, "narration": False}).json()
    assert est["total"] == 1.68 and est["film_seconds"] == 32
    with_voice = tc.post("/api/v1/movie/productions/estimate", json={**BODY, "scene_count": 4}).json()
    assert 0 < with_voice["narration"] < 0.05


def test_create_requires_login(client):
    tc, _app, _movie = client
    assert tc.post("/api/v1/movie/productions", json=BODY).status_code in (401, 403)


def test_produce_without_confirm_is_refused_with_estimate(client):
    tc, app, movie = client
    _login(app, movie)
    resp = tc.post("/api/v1/movie/productions", json={**BODY, "produce": True})
    assert resp.status_code == 400
    assert resp.json()["detail"]["estimate"]["total"] > 0


def test_plan_via_rest_then_produce_gate(client):
    tc, app, movie = client
    _login(app, movie)
    prod = tc.post("/api/v1/movie/productions", json=BODY).json()
    pid = prod["id"]
    for _ in range(50):
        status = tc.get(f"/api/v1/movie/productions/{pid}").json()
        if status["status"] == "planned":
            break
        time.sleep(0.1)
    assert status["status"] == "planned"
    assert status["scenes"][0]["visual_prompt"] == "a lighthouse at dusk"
    assert "script_raw" not in status
    assert tc.post(f"/api/v1/movie/productions/{pid}/produce", json={}).status_code == 400
    assert tc.get(f"/api/v1/movie/productions/{pid}/video").status_code == 404
    assert any(p["id"] == pid for p in tc.get("/api/v1/movie/productions").json())
    assert tc.get("/api/v1/movie/productions/notanid").status_code == 404


def test_mcp_tool_registered_and_gated(client):
    mcp_server = import_module("app.mcp_server")
    names = {t.name for t in asyncio.run(mcp_server.mcp.list_tools())}
    assert "movie_production" in names
    est = asyncio.run(mcp_server.movie_production(operation="estimate", scene_count=2, clip_seconds=4))
    assert est["success"] and est["estimate"]["film_seconds"] == 8
    missing = asyncio.run(mcp_server.movie_production(operation="produce"))
    assert not missing["success"] and "production_id" in missing["error"]
