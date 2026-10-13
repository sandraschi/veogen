"""API router aggregator - the missing wiring for the v3.1 salvage.

Each endpoint module in app/api/api_v1/endpoints/ defines a prefix-less
router. This aggregator mounts every module under /api/v1/<name> so the
frontend calls (e.g. /api/v1/chat/personas) finally reach the code.

Exclusions (documented):
- mcp_routes: spawns external MCP processes at import time; replaced by a
  real FastMCP surface in Phase 4.
- email_workflows: standalone /api/email system, no frontend consumer.
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    api_keys,
    auth,
    book,
    chat,
    code,
    compliance,
    enhanced_auth,
    flow,
    image,
    logs,
    movie,
    music,
    profile,
    prompt_coach,
    settings,
    sound_design,
    system,
    translation,
    video,
    workspace,
)

api_router = APIRouter(prefix="/api/v1")

# Auth
api_router.include_router(enhanced_auth.router, prefix="/enhanced-auth", tags=["auth"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Big Four media generation
api_router.include_router(video.router, prefix="/video", tags=["video"])
api_router.include_router(image.router, prefix="/image", tags=["image"])
api_router.include_router(music.router, prefix="/music", tags=["music"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(movie.router, prefix="/movie", tags=["movie"])

# User & settings
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
# api_keys routes are self-prefixed (/api-keys), so mount without a prefix
api_router.include_router(api_keys.router, tags=["api-keys"])

# System & observability
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])

# Feature modules
api_router.include_router(book.router, prefix="/book", tags=["book"])
api_router.include_router(code.router, prefix="/code", tags=["code"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(flow.router, prefix="/flow", tags=["flow"])
api_router.include_router(prompt_coach.router, prefix="/prompt-coach", tags=["prompt-coach"])
api_router.include_router(sound_design.router, prefix="/sound-design", tags=["sound-design"])
api_router.include_router(translation.router, prefix="/translation", tags=["translation"])
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
