# CLAUDE.md

Guidance for AI agents working in this repo.

## Project

VeoGen Industrial: AI media generation hub (video / music / image / chat /
movie scripts) on Google's Gemini family. Salvaged Aug 2026 from a
mid-2025 codebase - the REST API, auth, chat, and movie scripts are live;
media generation returns explicit `provider_not_wired` errors until model
IDs + a key are configured.

## Architecture

- **Backend** (`backend/`): FastAPI + SQLAlchemy (SQLite) on port **11150**.
  - `app/main.py` - app, `/health`, `/api/v1/diagnostics`, `/mcp` mount
  - `app/api/router.py` - v1 aggregator (19 endpoint modules)
  - `app/api/api_v1/endpoints/` - route modules (auth, chat, image, music, ...)
  - `app/services/` - business logic; `gemini_service.py` is the provider
    facade (chat real, media honest stubs)
  - `app/mcp_server.py` - FastMCP streamable HTTP surface
- **Frontend** (`frontend/`): React 18 + Vite + Tailwind + bun on port **11151**.
  - `src/App.js` - routes (29 pages); `src/services/` - API clients
  - `e2e/smoke.spec.ts` - Playwright suite (10 tests)
- **Ports**: 11150 backend / 11151 frontend (fleet registry).
- **Tooling**: `uv` (backend deps + lockfile), `bun` (frontend), `just`
  recipes (`serve`, `dev`, `test`, `lint`, `e2e`), `ruff` (correctness
  baseline: E4/E7/E9/F/I), Playwright for e2e.

## Commands

```powershell
just serve          # backend uvicorn on 11150
just dev            # frontend vite on 11151
just test           # backend pytest
just lint           # ruff check backend/app
just e2e            # Playwright smoke (backend+frontend auto-started)
```

## Rules

- API keys / model IDs live in `.env` (see `backend/.env.example`). Never
  commit `.env` or keys - the repo had a secret-leak purge in Phase 0.
- Media generation tools must return honest errors, never simulated output.
- New backend code: ruff-clean (F rules), FastAPI router mounted in
  `app/api/router.py`.
- New frontend code: JS/JSX with JSX-in-.js handled by the vite esbuild
  loader; `process.env.*` refs need entries in the vite `define` map.
- Keep `e2e/smoke.spec.ts` green before merging (`bunx playwright test`).

## Known limits

- Model IDs: single registry in `backend/app/config.py` (verified 2026-10-13).
  Never hardcode a model ID in a service; reference `settings.*_MODEL`.
- Text generation goes through `app/services/llm_providers.py` (local + cloud,
  selection in Settings). Media (Veo, TTS, Lyria) uses `google-genai` directly.
- Films: `app/services/movie_pipeline.py` (plan -> produce, confirm_cost gate).
  Single-clip `generate_video` / `generate_image` / `generate_music` MCP tools
  and the old per-feature media endpoints are still honest stubs.
- Some legacy services still import `google.generativeai` (EOL); new code uses
  `google.genai` or the provider layer.
- The Movie Maker route renders `pages/MovieMakerPage.js` (the legacy
  `components/movie/MovieMaker.jsx`, which called endpoints that never existed,
  was removed 2026-10-14).
- `llms-full.txt` is a generated corpus - regenerate after API changes.
