"""Model registry defaults + Lyria provider behaviour (offline, no API calls)."""

import asyncio
import base64
from types import SimpleNamespace

from app.config import Settings
from app.services import lyria_service

# Shut down per https://ai.google.dev/gemini-api/docs/models (checked 2026-10-13).
SHUT_DOWN_PREFIXES = ("gemini-1.5", "gemini-2.0-flash", "gemini-3-pro-preview", "imagen-4.0")


def test_registry_defaults_are_not_shut_down_models():
    s = Settings()
    ids = [v for k, v in vars(s).items() if k.endswith("_MODEL") and isinstance(v, str) and "-" in v]
    assert ids, "no model settings found"
    for model_id in ids:
        assert not model_id.startswith(SHUT_DOWN_PREFIXES), model_id


def _provider(tmp_path, monkeypatch, interaction):
    monkeypatch.setattr(lyria_service.settings, "OUTPUT_DIR", str(tmp_path))
    provider = lyria_service.LyriaProvider(api_key="test-key")
    calls = []

    def fake_create(**kwargs):
        calls.append(kwargs)
        return interaction

    provider.client = SimpleNamespace(interactions=SimpleNamespace(create=fake_create))
    return provider, calls


def test_lyria_saves_real_audio_and_picks_clip_model(tmp_path, monkeypatch):
    audio = b"ID3-fake-mp3-bytes"
    interaction = SimpleNamespace(
        output_audio=SimpleNamespace(data=base64.b64encode(audio).decode()), output_text="la la"
    )
    provider, calls = _provider(tmp_path, monkeypatch, interaction)

    result = asyncio.run(provider.generate_music("calm piano", duration_seconds=20))

    assert result["status"] == "success"
    assert result["model"] == lyria_service.settings.LYRIA_CLIP_MODEL
    assert calls[0]["model"] == lyria_service.settings.LYRIA_CLIP_MODEL
    with open(result["file_path"], "rb") as f:
        assert f.read() == audio
    assert result["lyrics"] == "la la"


def test_lyria_long_track_uses_full_model(tmp_path, monkeypatch):
    interaction = SimpleNamespace(output_audio=SimpleNamespace(data=base64.b64encode(b"x").decode()))
    provider, calls = _provider(tmp_path, monkeypatch, interaction)

    result = asyncio.run(provider.generate_music("epic score", duration_seconds=120))

    assert calls[0]["model"] == lyria_service.settings.LYRIA_MODEL
    assert result["duration"] == 120


def test_lyria_no_audio_is_an_error_not_a_fake_success(tmp_path, monkeypatch):
    provider, _ = _provider(tmp_path, monkeypatch, SimpleNamespace(output_audio=None))

    result = asyncio.run(provider.generate_music("anything"))

    assert result["status"] == "error"
    assert "audio_url" not in result
