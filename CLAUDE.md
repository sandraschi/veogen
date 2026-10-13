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
  - `e2e/smoke.spec.ts` - Playwright suite (6 tests)
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

- `google.generativeai` (legacy SDK) powers the chat engine and is EOL -
  migration to `google.genai` is future work.
- Media generation (video/image/music) needs current model IDs + a valid
  key; see `backend/.env.example`.
- `llms-full.txt` is a generated corpus - regenerate after API changes.
