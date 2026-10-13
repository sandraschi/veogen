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

from fastmcp import FastMCP

from app.api.api_v1.endpoints.movie import MovieScriptRequest, _parse_scenes, build_script_prompt
from app.config import settings
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
     "providers": {"chat": str, "video": str, "image": str, "music": str}}

    ## Examples
    veogen_status()
    """
    return {
        "success": True,
        "server": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mcp_tools": 6,
        "providers": {
            "chat": "wired",
            "video": "provider_not_wired",
            "image": "provider_not_wired",
            "music": "provider_not_wired",
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
