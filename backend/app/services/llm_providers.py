"""Unified local + cloud LLM providers for veogen's text features.

Ported from the fleet-canonical arxiv-mcp module (arxiv-mcp/src/arxiv_mcp/llm_providers.py,
spec arxiv-mcp/docs/SPEC-llm-providers.md; WEBAPP_SOTA_STANDARDS.md section VI.10):

- Provider IDs and key env names match the local-llm-mcp gateway.
- The browser never talks to a provider; everything goes through the backend.
- API keys live in a keystore (data/llm_keys.json, 0600, gitignored) or env vars,
  and env wins. GET responses only ever carry "configured" booleans.

veogen additions: optional temperature/max_tokens, a persisted provider/model
selection (data/llm_settings.json) and complete_text(), which chat, movie
scripts, book, code and the MCP script tool use. Media generation (Veo, Lyria,
image, TTS) stays on Google's native APIs and is not routed through here.
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

LOCAL_PROBE_TIMEOUT = 3.0
CLOUD_TIMEOUT = 30.0
CHAT_TIMEOUT = 120.0
KEYSTORE_NAME = "llm_keys.json"
SELECTION_NAME = "llm_settings.json"
ANTHROPIC_VERSION = "2023-06-01"
# Context window for local Ollama chat (long-ctx models would otherwise offload to CPU).
OLLAMA_NUM_CTX = 32768

PROVIDERS: tuple[dict[str, Any], ...] = (
    {
        "id": "ollama",
        "label": "Ollama",
        "kind": "local",
        "base_url": "http://127.0.0.1:11434",
        # Native API: /v1 ignores options such as num_ctx.
        "chat_path": "/api/chat",
        "models_path": "/api/tags",
        "tag_style": "ollama",
        "key_env": None,
        "curated": [],
    },
    {
        "id": "lmstudio",
        "label": "LM Studio",
        "kind": "local",
        "base_url": "http://127.0.0.1:1234",
        "chat_path": "/v1/chat/completions",
        "models_path": "/v1/models",
        "tag_style": "openai",
        "key_env": None,
        "curated": [],
    },
    {
        "id": "vllm",
        "label": "vLLM",
        "kind": "local",
        "base_url": "http://127.0.0.1:8000",
        "chat_path": "/v1/chat/completions",
        "models_path": "/v1/models",
        "tag_style": "openai",
        "key_env": None,
        "curated": [],
    },
    {
        "id": "google",
        "label": "Google Gemini",
        "kind": "cloud",
        # OpenAI-compatible endpoint (Bearer auth, /chat/completions, /models).
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "chat_path": "/chat/completions",
        "models_path": "/models",
        "tag_style": "openai",
        "key_env": "GEMINI_API_KEY",
        "key_env_fallbacks": ["GOOGLE_API_KEY"],
        # From the config registry (verified against ai.google.dev 2026-10-13).
        "curated": [settings.GEMINI_FLASH_MODEL, settings.GEMINI_PRO_MODEL, settings.GEMINI_FLASH_LITE_MODEL],
    },
    {
        "id": "openai",
        "label": "OpenAI",
        "kind": "cloud",
        "base_url": "https://api.openai.com/v1",
        "chat_path": "/chat/completions",
        "models_path": "/models",
        "tag_style": "openai",
        "key_env": "OPENAI_API_KEY",
        "curated": ["gpt-4o", "gpt-4o-mini"],
    },
    {
        "id": "anthropic",
        "label": "Anthropic",
        "kind": "cloud",
        "base_url": "https://api.anthropic.com",
        "chat_path": "/v1/messages",
        "models_path": "/v1/models",
        "tag_style": "anthropic",
        "key_env": "ANTHROPIC_API_KEY",
        "curated": ["claude-sonnet-5-5", "claude-opus-5-5", "claude-haiku-5-5", "claude-fable-5-1"],
    },
    {
        "id": "deepseek",
        "label": "DeepSeek",
        "kind": "cloud",
        # No /v1 prefix on this host.
        "base_url": "https://api.deepseek.com",
        "chat_path": "/chat/completions",
        "models_path": "/models",
        "tag_style": "openai",
        "key_env": "DEEPSEEK_API_KEY",
        "curated": ["deepseek-v4-flash", "deepseek-v4-pro"],
    },
    {
        "id": "openrouter",
        "label": "OpenRouter",
        "kind": "cloud",
        "base_url": "https://openrouter.ai/api/v1",
        "chat_path": "/chat/completions",
        "models_path": "/models",
        "tag_style": "openai",
        "key_env": "OPENROUTER_API_KEY",
        "curated": ["openrouter/auto"],
    },
    {
        "id": "meta",
        "label": "Meta",
        "kind": "cloud",
        "base_url": "https://api.meta.ai/v1",
        "chat_path": "/chat/completions",
        "models_path": "/models",
        "tag_style": "openai",
        "key_env": "MODEL_API_KEY",
        "curated": ["muse-spark-1.3-contributor", "muse-spark-1.3"],
    },
    {
        "id": "groq",
        "label": "Groq",
        "kind": "cloud",
        "base_url": "https://api.groq.com/openai/v1",
        "chat_path": "/chat/completions",
        "models_path": "/models",
        "tag_style": "openai",
        "key_env": "GROQ_API_KEY",
        "curated": ["llama-3.3-70b-versatile"],
    },
    {
        "id": "mistral",
        "label": "Mistral",
        "kind": "cloud",
        "base_url": "https://api.mistral.ai/v1",
        "chat_path": "/chat/completions",
        "models_path": "/models",
        "tag_style": "openai",
        "key_env": "MISTRAL_API_KEY",
        "curated": ["mistral-large-latest", "mistral-small-latest"],
    },
)

DEFAULT_SELECTION = {"provider": "google", "model": settings.GEMINI_FLASH_MODEL}


# --- registry ---------------------------------------------------------------


def get_provider(provider_id: str) -> dict[str, Any] | None:
    for row in PROVIDERS:
        if row["id"] == provider_id:
            return row
    return None


def require_provider(provider_id: str) -> dict[str, Any]:
    row = get_provider(provider_id)
    if row is None:
        known = ", ".join(r["id"] for r in PROVIDERS)
        raise ValueError(f"Unknown provider '{provider_id}'. Known: {known}")
    return row


# --- storage ----------------------------------------------------------------


def data_dir() -> Path:
    """backend/data by default (gitignored); VEOGEN_DATA_DIR overrides."""
    override = os.environ.get("VEOGEN_DATA_DIR", "").strip()
    path = Path(override) if override else Path(__file__).resolve().parents[2] / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read_json(name: str) -> dict[str, Any]:
    path = data_dir() / name
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("%s unreadable (%s); treating as empty", name, exc)
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(name: str, data: dict[str, Any], private: bool = False) -> None:
    path = data_dir() / name
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    if private:
        try:
            os.chmod(tmp, 0o600)
        except OSError:
            logger.debug("chmod 0600 failed (non-POSIX fs); continuing")
    os.replace(tmp, path)


def _read_keystore() -> dict[str, str]:
    return {k: v for k, v in _read_json(KEYSTORE_NAME).items() if isinstance(v, str) and v}


def get_key(provider_id: str) -> str:
    """Env var(s) first, then keystore. Empty when unset."""
    row = require_provider(provider_id)
    for env_name in [row.get("key_env"), *(row.get("key_env_fallbacks") or [])]:
        if env_name:
            value = os.environ.get(env_name, "").strip()
            if value:
                return value
    if provider_id == "google":
        # pydantic-settings reads .env into settings without exporting it to os.environ
        for value in (settings.GEMINI_API_KEY, settings.GOOGLE_API_KEY):
            if value and value.strip():
                return value.strip()
    return _read_keystore().get(provider_id, "")


def is_configured(provider_id: str) -> bool:
    row = require_provider(provider_id)
    return row["kind"] == "local" or bool(get_key(provider_id))


def keys_configured() -> dict[str, bool]:
    return {r["id"]: is_configured(r["id"]) for r in PROVIDERS if r["kind"] == "cloud"}


def save_key(provider_id: str, api_key: str) -> None:
    row = require_provider(provider_id)
    if row["kind"] != "cloud":
        raise ValueError(f"Provider '{provider_id}' takes no API key")
    key = (api_key or "").strip()
    if not key:
        raise ValueError("Empty API key")
    entries = _read_keystore()
    entries[provider_id] = key
    _write_json(KEYSTORE_NAME, entries, private=True)


def delete_key(provider_id: str) -> bool:
    require_provider(provider_id)
    entries = _read_keystore()
    if provider_id not in entries:
        return False
    del entries[provider_id]
    _write_json(KEYSTORE_NAME, entries, private=True)
    return True


def get_selection() -> dict[str, str]:
    """Active provider/model for text features (persisted, defaults to Gemini Flash)."""
    stored = _read_json(SELECTION_NAME)
    provider = str(stored.get("provider") or DEFAULT_SELECTION["provider"])
    model = str(stored.get("model") or "")
    if get_provider(provider) is None:
        provider = DEFAULT_SELECTION["provider"]
    if not model:
        model = DEFAULT_SELECTION["model"] if provider == DEFAULT_SELECTION["provider"] else ""
    return {"provider": provider, "model": model}


def save_selection(provider_id: str, model: str) -> dict[str, str]:
    require_provider(provider_id)
    model = (model or "").strip()
    if not model:
        raise ValueError("Empty model name")
    _write_json(SELECTION_NAME, {"provider": provider_id, "model": model})
    return get_selection()


def public_provider_info() -> list[dict[str, Any]]:
    """Registry rows safe for GET responses: capability flags, never key bytes."""
    return [
        {
            "id": r["id"],
            "label": r["label"],
            "kind": r["kind"],
            "base_url": r["base_url"],
            "needs_key": r["kind"] == "cloud",
            "key_env": r.get("key_env"),
            "configured": is_configured(r["id"]),
        }
        for r in PROVIDERS
    ]


# --- models -----------------------------------------------------------------


def _parse_model_list(tag_style: str, payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return []
    if tag_style == "ollama":
        models = payload.get("models") or []
        return [m.get("name", "") for m in models if isinstance(m, dict) and m.get("name")]
    data = payload.get("data") or []
    ids = [m.get("id", "") for m in data if isinstance(m, dict) and m.get("id")]
    # Google's compat list prefixes ids with "models/"; chat accepts the bare id.
    return [i.removeprefix("models/") for i in ids]


async def probe_local(provider_id: str) -> tuple[bool, list[str]]:
    row = require_provider(provider_id)
    if row["kind"] != "local":
        raise ValueError(f"Provider '{provider_id}' is not local")
    try:
        async with httpx.AsyncClient(timeout=LOCAL_PROBE_TIMEOUT) as client:
            resp = await client.get(row["base_url"] + row["models_path"])
    except Exception as exc:
        logger.debug("local probe %s failed: %s", provider_id, exc)
        return False, []
    if resp.status_code >= 500:
        return False, []
    try:
        return True, _parse_model_list(row["tag_style"], resp.json())
    except Exception:
        return True, []


async def list_models(provider_id: str, api_key: str = "") -> dict[str, Any]:
    """Model list with source flag. Unkeyed clouds return curated names with key_missing=True."""
    row = require_provider(provider_id)
    if row["kind"] == "local":
        reachable, models = await probe_local(provider_id)
        return {"provider": provider_id, "models": models, "source": "live" if reachable else "none"}
    key = (api_key or "").strip() or get_key(provider_id)
    if not key:
        return {
            "provider": provider_id,
            "models": list(row["curated"]),
            "source": "curated",
            "key_missing": True,
            "note": "Save a key for the live list.",
        }
    try:
        async with httpx.AsyncClient(timeout=CLOUD_TIMEOUT) as client:
            resp = await client.get(row["base_url"] + row["models_path"], headers=_auth_headers(row, key))
            resp.raise_for_status()
            models = _parse_model_list(row["tag_style"], resp.json())
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        logger.warning("live model list for %s HTTP %s; curated fallback", provider_id, status)
        error = (
            f"{row['label']} rejected the key (HTTP {status})."
            if status in (401, 403)
            else f"{row['label']} HTTP {status}."
        )
        return {"provider": provider_id, "models": list(row["curated"]), "source": "curated", "error": error}
    except Exception as exc:
        logger.warning("live model list for %s failed (%s); curated fallback", provider_id, exc)
        return {"provider": provider_id, "models": list(row["curated"]), "source": "curated"}
    if not models:
        return {"provider": provider_id, "models": list(row["curated"]), "source": "curated"}
    return {"provider": provider_id, "models": models, "source": "live"}


# --- chat -------------------------------------------------------------------


def _auth_headers(row: dict[str, Any], api_key: str) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if row["id"] == "anthropic":
        headers["x-api-key"] = api_key
        headers["anthropic-version"] = ANTHROPIC_VERSION
    elif row["id"] == "openrouter":
        headers["Authorization"] = f"Bearer {api_key}"
        headers["HTTP-Referer"] = "http://127.0.0.1:11151/"
        headers["X-Title"] = "veogen"
    elif row["kind"] == "cloud":
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _build_request(
    row: dict[str, Any],
    model: str,
    messages: list[dict[str, Any]],
    temperature: float | None,
    max_tokens: int | None,
    stream: bool,
) -> dict[str, Any]:
    if row["id"] == "anthropic":
        system_parts = [str(m.get("content", "")) for m in messages if m.get("role") == "system"]
        converted = [
            {
                "role": m.get("role") if m.get("role") in ("user", "assistant") else "user",
                "content": str(m.get("content", "")),
            }
            for m in messages
            if m.get("role") != "system"
        ]
        body: dict[str, Any] = {"model": model, "max_tokens": max_tokens or 1024, "messages": converted}
        if system_parts:
            body["system"] = "\n\n".join(system_parts)
        if temperature is not None:
            body["temperature"] = temperature
    elif row["id"] == "ollama":
        options: dict[str, Any] = {"num_ctx": OLLAMA_NUM_CTX}
        if temperature is not None:
            options["temperature"] = temperature
        if max_tokens:
            options["num_predict"] = max_tokens
        body = {
            "model": model,
            "messages": [{"role": m.get("role", "user"), "content": str(m.get("content", ""))} for m in messages],
            "options": options,
        }
    else:
        body = {"model": model, "messages": messages}
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens:
            body["max_tokens"] = max_tokens
    body["stream"] = stream
    return body


def _resolve(provider_id: str, model: str) -> tuple[dict[str, Any], str]:
    row = require_provider(provider_id)
    if not (model or "").strip():
        raise ValueError("Empty model name")
    key = get_key(provider_id) if row["kind"] == "cloud" else ""
    if row["kind"] == "cloud" and not key:
        raise ValueError(f"Provider '{provider_id}' has no API key configured")
    return row, key


async def chat_complete(
    provider_id: str,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Non-streaming chat via the backend proxy. Returns assistant text."""
    row, key = _resolve(provider_id, model)
    body = _build_request(row, model, messages, temperature, max_tokens, stream=False)
    try:
        async with httpx.AsyncClient(timeout=CHAT_TIMEOUT) as client:
            resp = await client.post(row["base_url"] + row["chat_path"], json=body, headers=_auth_headers(row, key))
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        raise RuntimeError(f"Provider '{provider_id}' HTTP {status}") from exc
    except Exception as exc:
        raise RuntimeError(f"Provider '{provider_id}' unreachable ({type(exc).__name__})") from exc
    if row["id"] == "anthropic":
        blocks = data.get("content") or []
        return "".join(b.get("text", "") for b in blocks if isinstance(b, dict) and b.get("type") == "text")
    if row["id"] == "ollama":
        return str((data.get("message") or {}).get("content", ""))
    try:
        return data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Provider '{provider_id}' returned an unexpected body") from exc


def _openai_sse_chunk(model: str, text: str) -> bytes:
    chunk = {"object": "chat.completion.chunk", "model": model, "choices": [{"index": 0, "delta": {"content": text}}]}
    return ("data: " + json.dumps(chunk) + "\n\n").encode("utf-8")


async def chat_stream(
    provider_id: str,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> AsyncIterator[bytes]:
    """Streaming chat as OpenAI-style SSE bytes, normalized for every provider."""
    row, key = _resolve(provider_id, model)
    body = _build_request(row, model, messages, temperature, max_tokens, stream=True)
    headers = _auth_headers(row, key)
    headers["Accept"] = "text/event-stream"
    async with httpx.AsyncClient(timeout=CHAT_TIMEOUT) as client:
        async with client.stream("POST", row["base_url"] + row["chat_path"], json=body, headers=headers) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if row["id"] == "ollama":
                    try:
                        event = json.loads(line) if line.strip() else {}
                    except json.JSONDecodeError:
                        continue
                    text = "" if event.get("done") else str((event.get("message") or {}).get("content", ""))
                    if text:
                        yield _openai_sse_chunk(model, text)
                elif row["id"] == "anthropic":
                    if not line.startswith("data: "):
                        continue
                    try:
                        event = json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue
                    if event.get("type") == "content_block_delta":
                        text = (event.get("delta") or {}).get("text", "")
                        if text:
                            yield _openai_sse_chunk(model, text)
                elif line.startswith("data: ") and line.strip() != "data: [DONE]":
                    yield (line + "\n\n").encode("utf-8")
    yield b"data: [DONE]\n\n"


async def complete_text(
    prompt: str,
    system: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    history: list[dict[str, Any]] | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> str:
    """One-shot text generation with the active selection (or an explicit provider/model)."""
    selection = get_selection()
    provider_id = provider or selection["provider"]
    model_name = model or (selection["model"] if provider_id == selection["provider"] else "")
    if not model_name:
        raise ValueError(f"No model selected for provider '{provider_id}' - choose one in Settings")
    messages: list[dict[str, Any]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.extend(history or [])
    messages.append({"role": "user", "content": prompt})
    return await chat_complete(provider_id, model_name, messages, temperature=temperature, max_tokens=max_tokens)


def onboarding_state(locals_detected: dict[str, bool]) -> dict[str, Any]:
    """Starter-path recommendation: detected local first, else a configured cloud, else Google key."""
    clouds = keys_configured()
    if any(locals_detected.values()):
        first = next(p for p, ok in locals_detected.items() if ok)
        path = {"provider": first, "why": "Local engine detected - free and private."}
    elif any(clouds.values()):
        first = next(p for p, ok in clouds.items() if ok)
        path = {"provider": first, "why": "A cloud key is already configured."}
    else:
        path = {
            "provider": "google",
            "why": "veogen's media features need a Gemini key anyway; paste it once in Settings. "
            "Or install Ollama for free local text generation.",
        }
    return {"locals": locals_detected, "clouds": clouds, "selection": get_selection(), "recommended": path}
