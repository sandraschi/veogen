"""FastMCP server surface for VeoGen (Phase 4 fleet integration).

Serves MCP streamable HTTP on the same FastAPI app at /mcp, exposing a
small tool set:

- status: server + provider state
- list_personas: real chat personas (from persona_chat_service)
- movie_script: REAL script generation via Gemini (same pipeline as the
  REST endpoint)
- generate_video / generate_image / generate_music: honest
  provider_not_wired errors until media providers are wired with a valid
  key + current model IDs (see config.py GEMINI_*/VEO_*/LYRIA_*/IMAGEN_*)
"""

from typing import Literal, Optional

from fastmcp import FastMCP

from app.api.api_v1.endpoints.movie import MovieScriptRequest, _parse_scenes, build_script_prompt
from app.config import settings
from app.services import llm_providers, movie_pipeline
from app.services.gemini_service import gemini_service
from app.services.persona_chat_service import persona_chat_service

mcp = FastMCP("veogen-mcp")

_READ_ONLY = {"readonly": True}
_MUTATING = {}


@mcp.tool(annotations=_READ_ONLY)
def veogen_status() -> dict:
    """Return VeoGen server status: version, registered tools, provider state.

    ## Return Format
    {"success": bool, "server": str, "version": str, "mcp_tools": int,
     "providers": {"chat": str, "movie_production": str, "video": str, "image": str, "music": str}}

    ## Examples
    veogen_status()
    """
    selection = llm_providers.get_selection()
    return {
        "success": True,
        "server": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mcp_tools": 7,
        "providers": {
            "chat": f"{selection['provider']} / {selection['model']}",
            "movie_production": f"wired ({settings.VEO_LITE_MODEL} / {settings.VEO_MODEL}, {settings.LYRIA_MODEL})",
            "video": "provider_not_wired (single clips; use movie_production)",
            "image": "provider_not_wired",
            "music": "provider_not_wired (single tracks; movie_production scores films)",
        },
    }


@mcp.tool(annotations=_READ_ONLY)
def list_personas() -> dict:
    """List the available chat personas with their expertise.

    ## Return Format
    {"success": bool, "personas": [{"id": str, "name": str, "description": str,
     "personality": str, "expertise": list[str]}]}

    ## Examples
    list_personas()
    """
    personas = persona_chat_service.get_available_personas()
    return {
        "success": True,
        "personas": [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "description": p.get("description"),
                "personality": p.get("personality"),
                "expertise": p.get("expertise", []),
            }
            for p in personas
        ],
    }


@mcp.tool(annotations=_MUTATING)
async def movie_script(
    title: str,
    concept: str,
    style: str = "cinematic",
    max_clips: int = 10,
    budget: float = 5.0,
) -> dict:
    """Generate a full movie script with scenes via Gemini.

    Requires a configured Gemini API key (GEMINI_API_KEY or GOOGLE_API_KEY)
    and current model settings.

    ## Return Format
    {"success": bool, "script": str, "scenes": [{"id": int, "title": str,
     "description": str, "duration": int, "prompt": str}]}

    ## Examples
    movie_script(title="The Last Transmission", concept="A radio operator on a
        dying space station hears one final signal from Earth.", max_clips=6)
    """
    request = MovieScriptRequest(
        title=title,
        concept=concept,
        style=style,
        preset="short-film",
        max_clips=max_clips,
        budget=budget,
    )
    try:
        text = await gemini_service.generate_text(build_script_prompt(request))
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "error_type": "provider_not_wired",
            "suggestions": [
                "Set GEMINI_API_KEY or GOOGLE_API_KEY in .env",
                "Verify model IDs in config.py GEMINI_*/VEO_*/LYRIA_*/IMAGEN_* settings",
            ],
        }
    return {"success": True, "script": text, "scenes": [s.model_dump() for s in _parse_scenes(text, max_clips)]}


_PAID = {"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True}


@mcp.tool(annotations=_PAID)
async def movie_production(
    operation: Literal["estimate", "plan", "produce", "status", "list", "cancel"],
    production_id: Optional[str] = None,
    title: Optional[str] = None,
    concept: Optional[str] = None,
    style: str = "cinematic",
    scene_count: int = 4,
    clip_seconds: Literal[4, 6, 8] = 8,
    tier: Literal["lite", "standard"] = "lite",
    resolution: Literal["720p", "1080p"] = "720p",
    aspect_ratio: Literal["16:9", "9:16"] = "16:9",
    narration: bool = True,
    music: bool = True,
    confirm_cost: bool = False,
) -> dict:
    """Make a short film end to end: LLM script -> Veo 3.1 clips -> TTS narration -> Lyria score -> ffmpeg.

    [RATIONALE] One portmanteau for the whole workflow so the paid step stays behind an
    explicit two-step guardrail: plan first (one text call, free media-wise), read the
    estimate, then produce with confirm_cost=True.

    Operations:
    - estimate: price a film from the parameters, no API call (title/concept not needed).
    - plan: needs title + concept; writes the script with the LLM selected in Settings and
      returns a production_id with status "planned" and a priced estimate (runs in background,
      poll with status).
    - produce: needs production_id and confirm_cost=True; generates media for a planned
      production (also resumes failed / interrupted / cancelled ones, reusing finished clips).
    - status: needs production_id; progress 0-100, step, scenes, estimate, video_path.
    - list: recent productions (bounded: newest 50).
    - cancel: needs production_id; stops before the next paid call.

    Costs (Google list prices, 2026-10-13): Veo 3.1 Lite $0.05/s (720p), Standard $0.40/s;
    Lyria $0.04 clip / $0.08 song. Clips are 4, 6 or 8 s with native audio.

    ## Return Format
    {"success": bool, "production": {...} | None, "productions": [...] | None,
     "estimate": {...} | None, "error": str | None, "suggestions": [str] | None}

    ## Examples
    movie_production(operation="estimate", scene_count=4, clip_seconds=8)
    movie_production(operation="plan", title="Dawn Fox", concept="A red fox greets the first morning of spring.")
    movie_production(operation="produce", production_id="0a1b2c3d4e5f", confirm_cost=True)
    """
    try:
        if operation == "estimate":
            return {
                "success": True,
                "estimate": movie_pipeline.estimate(scene_count, clip_seconds, tier, resolution, narration, music),
            }
        if operation == "list":
            return {"success": True, "productions": movie_pipeline.list_productions()[:50]}
        if operation == "plan":
            if not title or not concept or len(concept) < 20:
                return {"success": False, "error": "plan needs title and a concept of at least 20 characters"}
            prod = movie_pipeline.create(
                {
                    "title": title,
                    "concept": concept,
                    "style": style,
                    "scene_count": max(1, min(scene_count, 12)),
                    "clip_seconds": clip_seconds,
                    "tier": tier,
                    "resolution": resolution,
                    "aspect_ratio": aspect_ratio,
                    "narration": narration,
                    "music": music,
                }
            )
            movie_pipeline.start(prod["id"], produce=False)
            return {"success": True, "production": prod, "message": "Planning started; poll operation='status'."}
        if not production_id:
            return {"success": False, "error": f"{operation} needs production_id"}
        prod = movie_pipeline.load(production_id)
        if operation == "status":
            prod.pop("script_raw", None)
            return {"success": True, "production": prod}
        if operation == "cancel":
            return {"success": True, "production": movie_pipeline.cancel(production_id)}
        if not confirm_cost:
            return {
                "success": False,
                "error": "confirm_cost required",
                "estimate": prod["estimate"],
                "suggestions": [
                    f"This film costs about ${prod['estimate']['total']}; call again with confirm_cost=True"
                ],
            }
        movie_pipeline.start(production_id, produce=True)
        return {"success": True, "production": movie_pipeline.load(production_id), "message": "Production started."}
    except KeyError:
        return {"success": False, "error": f"Unknown production_id '{production_id}'"}
    except (RuntimeError, ValueError) as exc:
        return {"success": False, "error": str(exc)}


@mcp.tool(annotations=_MUTATING)
async def generate_video(prompt: str, duration: int = 5, style: str = "cinematic") -> dict:
    """Generate a video. Not wired in this build - returns an explicit error.

    ## Return Format
    {"success": bool, "error": str | None, "error_type": str | None}

    ## Examples
    generate_video(prompt="a robot dancing in a neon garage")
    """
    return await gemini_service.generate_video(prompt=prompt, duration=duration, style=style)


@mcp.tool(annotations=_MUTATING)
async def generate_image(prompt: str, style: str = "photorealistic") -> dict:
    """Generate an image. Not wired in this build - returns an explicit error.

    ## Return Format
    {"success": bool, "error": str | None, "error_type": str | None}

    ## Examples
    generate_image(prompt="a cyberpunk city at sunset")
    """
    return await gemini_service.generate_image(prompt=prompt, style=style)


@mcp.tool(annotations=_MUTATING)
async def generate_music(prompt: str, genre: str = "ambient") -> dict:
    """Generate music. Not wired in this build - returns an explicit error.

    ## Return Format
    {"success": bool, "error": str | None, "error_type": str | None}

    ## Examples
    generate_music(prompt="a calm forest morning", genre="ambient")
    """
    return await gemini_service.generate_music(prompt=prompt, style=genre)


def mcp_http_app():
    """Starlette app mountable at /mcp on the main FastAPI app.

    http_app(path='/') serves the MCP endpoint at '/' so the FastAPI
    mount at /mcp resolves to /mcp/ (streamable HTTP).
    """
    return mcp.http_app(path="/")
