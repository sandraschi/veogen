# VeoGen Industrial

AI media generation hub: video, music, image, chat, and movie-script
tooling on Google's Gemini model family.

> **Status**: a mid-2025 codebase salvaged in Aug 2026, polished Oct 2026.
> Auth, chat (any local or cloud LLM), and the full movie workflow
> (script -> Veo 3.1 clips -> narration -> Lyria score -> stitched MP4) are
> live. Single-clip video/image/music endpoints still return explicit
> `provider_not_wired` errors - no fake output is served anywhere.

## Quick start

```powershell
./start.ps1          # full stack: backend + frontend + browser
# or piecemeal:
just serve           # backend on http://127.0.0.1:11150
just dev             # frontend on http://127.0.0.1:11151
just test            # backend pytest
just e2e             # Playwright smoke (10 tests)
```

## Stack

| Layer | Tech | Port |
|-------|------|------|
| Backend | FastAPI + SQLAlchemy (SQLite) + FastMCP | 11150 |
| MCP surface | FastMCP 3.4 streamable HTTP at `/mcp` | 11150 |
| Frontend | React 18 + Vite + Tailwind + bun | 11151 |

Ports registered in `mcp-central-docs/operations/WEBAPP_PORTS.md`.

## What works

- **Auth**: register / login / JWT / profile / settings (SQLite-backed)
- **Text AI, local or cloud**: Settings -> "Text AI" picks the model for
  chat, movie scripts, book, code and translation - Ollama, LM Studio, vLLM
  (free, local) or Google Gemini, OpenAI, Anthropic, DeepSeek, OpenRouter,
  Meta, Groq, Mistral. Default: `gemini-3.8-flash`. Keys are stored
  server-side and never returned (`/api/llm/*`, `/api/settings/llm`).
- **Movie Maker** (`/moviemaker`, `POST /api/v1/movie/productions`):
  1. *Plan* - your text model writes a shot list (visual prompt + narration
     per scene) and the app prices it. No media cost.
  2. *Produce* - after you confirm the price: one Veo 3.1 clip per scene
     (4/6/8 s with native audio; Lite $0.05/s or Standard $0.40/s at 720p),
     Gemini TTS narration, a Lyria score, stitched by ffmpeg into one MP4.
     Background job with progress, cancel and resume.
- **Chat**: persona chat over the selected text model
- **REST surface**: ~110 routes under `/api/v1` and `/api` (OpenAPI at `/docs`)
- **MCP tools**: `veogen_status`, `list_personas`, `movie_script`,
  `movie_production` (estimate/plan/produce/status/list/cancel),
  `generate_video` / `generate_image` / `generate_music` (honest stubs)
- **Observability**: `/health`, `/api/v1/diagnostics` (fleet-standard)

## Models

All Google model IDs live in `backend/app/config.py` (verified against
ai.google.dev on 2026-10-13) and can be overridden in `.env`:
`gemini-3.8-flash`, `gemini-3.1-pro-preview`, `gemini-3.5-flash-lite`,
`gemini-3.8-flash-tts`, `veo-3.1-generate-preview`,
`veo-3.1-lite-generate-preview`, `lyria-3.5`, `lyria-3-clip-preview`,
`gemini-3.1-flash-image`.

## What needs your key

Movie production and the Google text model need a Gemini API key: paste it
in Settings -> Text AI -> Google, or set `GEMINI_API_KEY` in `.env` (see
`backend/.env.example`). Local text models need no key. Movie production
also needs `ffmpeg` on PATH.

## Tests

```powershell
cd backend; uv run pytest      # 33 backend tests (offline, no paid calls)
cd frontend; bunx playwright test   # 10 e2e tests (incl. authenticated nav walk)
```

## Repo layout

```
backend/    FastAPI app (app/), tests, pyproject.toml + uv.lock
frontend/   React app (src/), bun.lock, Playwright e2e/
docs/       design docs (some stale - see llms.txt)
_archive/   quarantined legacy files from the salvage (gitignored)
```
