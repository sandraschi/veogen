"""Movie Maker API endpoints - real script generation (Phase 3 salvage).

The frontend Movie Maker used to generate mock scripts client-side. This
endpoint generates the script server-side through the real Gemini chat
provider. Video rendering is not wired in this build (media providers
pending); the script step is fully functional.
"""

import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user_optional
from app.database import User
from app.services.gemini_service import gemini_service

router = APIRouter()


class MovieScriptRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Movie title.")
    concept: str = Field(..., min_length=20, max_length=2000, description="Plot / concept.")
    style: str = Field("cinematic", description="Visual style id.")
    preset: str = Field("short-film", description="Length preset id.")
    max_clips: int = Field(10, ge=3, le=50, description="Target scene count.")
    budget: float = Field(5.0, ge=1, le=100, description="Budget in dollars.")


class MovieScene(BaseModel):
    id: int
    title: str
    description: str
    duration: int = 8
    prompt: str


class MovieScriptResponse(BaseModel):
    status: str
    script: str
    scenes: List[MovieScene] = []
    message: Optional[str] = None


_SCENE_RE = re.compile(r"^#{1,3}\s+scene\s+(\d+)\s*$", re.IGNORECASE)


def _parse_scenes(text: str, max_clips: int) -> List[MovieScene]:
    """Best-effort parse of '### Scene N' markdown sections into scene cards."""
    scenes: List[MovieScene] = []
    blocks = re.split(r"(?m)^#{1,3}\s+scene\s+\d+\s*$", text, flags=re.IGNORECASE)
    headings = re.findall(r"(?m)^#{1,3}\s+scene\s+(\d+)\s*$", text, re.IGNORECASE)
    for idx, (num, block) in enumerate(zip(headings, blocks[1:]), start=1):
        if len(scenes) >= max_clips:
            break
        lines = [ln.replace("**", "").strip(" -").strip() for ln in block.strip().splitlines() if ln.strip()]
        description = next(
            (ln for ln in lines if not ln.lower().startswith(("duration", "visual prompt", "prompt", "continuity"))),
            "",
        )
        prompt = next(
            (ln for ln in lines if ln.lower().startswith(("visual prompt", "prompt"))),
            description,
        )
        duration_match = re.search(r"duration[:\s]*(\d+)", block, re.IGNORECASE)
        scenes.append(
            MovieScene(
                id=int(num) if num.isdigit() else idx,
                title=f"Scene {int(num) if num.isdigit() else idx}",
                description=description[:300] if description else "",
                duration=int(duration_match.group(1)) if duration_match else 8,
                prompt=prompt[:500] if prompt else "",
            )
        )
    return scenes


def build_script_prompt(request: MovieScriptRequest) -> str:
    """Shared prompt template for script generation (REST + MCP surfaces)."""
    return (
        f"Write a short film script.\n"
        f"Title: {request.title}\n"
        f"Concept: {request.concept}\n"
        f"Visual style: {request.style}\n"
        f"Target: {request.max_clips} scenes, budget ${request.budget:.0f}\n\n"
        "Return markdown with a '## Synopsis' section and one '### Scene N' "
        "section per scene containing Duration, Description and Visual Prompt lines."
    )


@router.post("/generate-script", response_model=MovieScriptResponse)
async def generate_script(
    request: MovieScriptRequest,
    current_user: User = Depends(get_current_user_optional),
):
    """Generate a full movie script with scenes via the Gemini provider."""
    try:
        text = await gemini_service.generate_text(build_script_prompt(request))
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Script generation unavailable - check GEMINI_API_KEY/GOOGLE_API_KEY and model settings. ({e})",
        )

    scenes = _parse_scenes(text, request.max_clips)
    return MovieScriptResponse(status="success", script=text, scenes=scenes)
