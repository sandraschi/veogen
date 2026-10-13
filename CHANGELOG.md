# Changelog

## [3.2.0] - 2026-10-13

### Models
- One model registry in `backend/app/config.py`, verified against
  ai.google.dev/gemini-api/docs/models: `gemini-3.8-flash` (default text),
  `gemini-3.1-pro-preview`, `gemini-3.5-flash-lite`, `gemini-3.8-flash-tts`,
  `veo-3.1-generate-preview` / `veo-3.1-lite-generate-preview`, `lyria-3.5` /
  `lyria-3-clip-preview`, `gemini-3.1-flash-image`. Shut-down IDs (1.5, 2.0,
  3.0, Imagen 4) removed from all services.
- `google-genai` >= 2.25 (2.30.1 locked) for the Interactions API.

### Local + cloud LLM
- Provider layer (fleet contract, ported from arxiv-mcp): Ollama, LM Studio,
  vLLM, Google, OpenAI, Anthropic, DeepSeek, OpenRouter, Meta, Groq, Mistral.
  Routes `/api/llm/*` + `/api/settings/llm`; keys write-only.
- Chat, movie scripts, book, code, translation and the MCP script tool use the
  provider selected in Settings (default Gemini Flash).
- Settings: "Text AI (local + cloud)" panel with provider cards.

### Movie production workflow
- Plan (LLM shot list + priced estimate) -> produce (Veo clips, TTS narration,
  Lyria score, ffmpeg stitch) as a background job with progress, cancel and
  resume; produce requires `confirm_cost`. REST `/api/v1/movie/productions*`,
  MCP `movie_production`, rewritten Movie Maker page.

### Fixes
- Lyria provider returned a fixed sample URL as success; movie script fallback
  returned a canned template; legacy Veo/Gemini video path wrote placeholder
  bytes as `.mp4`. All removed - failures are reported.
- `book` / `code` endpoints awaited a sync method (TypeError on every call).
- `.gitignore` to fleet standard; `frontend/biome.json` key fixed so the lint
  gate runs (reports 389 pre-existing findings).

## [3.1.1-salvage] - 2026-08-04

### Salvage (Phases 0-4)
- **Decontaminated**: purged committed secrets (API keys, login creds, emails,
  user DB) from git history; rotated-key reminder in `.env.example`
- **Rewired**: 19 endpoint modules mounted under `/api/v1` (were orphaned -
  app served 0 API routes); SQLite replaces the unwired Postgres/Redis/Celery
  stack; `init_db()` enabled
- **Ports**: 7655/4700/10730/10731 → **11150/11151** everywhere (10730 was
  registered to another fleet repo)
- **Real features**: movie script generation via Gemini (no more client-side
  mock scripts); lazy provider so the app boots without a key; honest
  provider-not-wired errors instead of simulated media output
- **Frontend builds**: CRA→Vite (index.html, esbuild jsx, postcss .cjs),
  lucide/heroicons renames, process.env define map, bun migration
- **FastMCP surface**: streamable HTTP at `/mcp` with 6 tools
- **CI**: lint + typecheck + pytest + Playwright e2e on every push
- **Docs**: honest README, llms.txt fixed, glama.json

## [3.1.0-industrial] - 2026-04-18

### 🚀 Industrial Revolution
- **SOTA Stack Migration**: Upgraded total infrastructure to April 2026 standards.
- **Frontend Vite Migration**: Removed `create-react-app` in favor of Vite 5 (10x faster HMR).
- **React 18.3+**: Modernized core components and hooks.
- **Fleet Port Standardization**: Shifted backend to `10730` and frontend to `10731` for Registry compliance.

### 🤖 AI Models (v3.1)
- **Gemini 3.1 Pro/Flash**: Complete integration with thinking-level controls.
- **Nano Banana 2**: Implemented the new Gemini 3.1 Flash Image model for ultra-fast Image generation with search grounding.
- **Flash TTS**: Native Gemini 3.1 TTS integration with natural prosody and audio tags.
- **Veo 3.1**: Advanced video generation with cinematic continuity.
- **Lyria 3**: High-fidelity music composition system.

### 🎨 Design & UX
- **Glassmorphism Premium**: Total UI overhaul using modern translucent design tokens.
- **Studio Hierarchy**: Streamlined the 25+ legacy routes into the "Big Four" core studios and a collapsible "Lab" for experimental tools.
- **Motion System**: Implemented high-fidelity Framer Motion transitions.

### 🛠️ Tooling & DX
- **Biome Integration**: Strict linting and formatting for the frontend (0-error standard).
- **FastMCP 3.2**: Upgraded MCP integration for modern bridge protocols.
- **JUST / PS1 Start**: Standardized startup patterns.

### 🧹 The Great Purge
- Deleted 30+ junk files (`_broken`, `_backup`, `_corrupted`).
- Archived "gaslight" placeholder routes.
- Removed legacy `setup.sh`/`setup.bat`.

## [2.0.0] - 2025-10-15
- Legacy "Movie Maker" version. (Outdated)
