"""Movie Maker API endpoints - real script generation (Phase 3 salvage).

The frontend Movie Maker used to generate mock scripts client-side. This
endpoint generates the script server-side through the real Gemini chat
provider. Video rendering is not wired in this build (media providers
pending); the script step is fully functional.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.api.deps import get_current_user, get_current_user_optional
from app.database import User
from app.services import movie_pipeline
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


# --- Production workflow: plan (script + estimate) -> produce (Veo, TTS, Lyria, ffmpeg) ---


class ProductionRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    concept: str = Field(..., min_length=20, max_length=2000)
    style: str = Field("cinematic", max_length=60)
    scene_count: int = Field(4, ge=1, le=12)
    clip_seconds: Literal[4, 6, 8] = 8
    tier: Literal["lite", "standard"] = Field("lite", description="Veo 3.1 Lite ($0.05/s) or Standard ($0.40/s)")
    resolution: Literal["720p", "1080p"] = "720p"
    aspect_ratio: Literal["16:9", "9:16"] = "16:9"
    narration: bool = True
    voice: str = Field("Kore", max_length=40)
    music: bool = True
    produce: bool = Field(False, description="False: plan only (script + estimate). True: also generate media.")
    confirm_cost: bool = Field(False, description="Required with produce=True: acknowledges the estimate.")


class ProduceRequest(BaseModel):
    confirm_cost: bool = False


def _get_production(production_id: str) -> Dict[str, Any]:
    try:
        return movie_pipeline.load(production_id)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Production not found")


def _cost_gate(confirm: bool, est: Dict[str, Any]) -> None:
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "confirm_cost required",
                "message": f"Producing this film costs about ${est['total']} (Google list prices). "
                "Resend with confirm_cost=true to proceed.",
                "estimate": est,
            },
        )


@router.post("/productions/estimate")
async def estimate_production(request: ProductionRequest) -> Dict[str, Any]:
    """Price a production without any API call."""
    return movie_pipeline.estimate(
        request.scene_count, request.clip_seconds, request.tier, request.resolution, request.narration, request.music
    )


@router.post("/productions")
async def create_production(request: ProductionRequest, current_user: User = Depends(get_current_user)):
    """Create a production and start planning (and producing, when produce + confirm_cost)."""
    est = movie_pipeline.estimate(
        request.scene_count, request.clip_seconds, request.tier, request.resolution, request.narration, request.music
    )
    if request.produce:
        _cost_gate(request.confirm_cost, est)
    prod = movie_pipeline.create(request.model_dump())
    movie_pipeline.start(prod["id"], produce=request.produce)
    return movie_pipeline.load(prod["id"])


@router.post("/productions/{production_id}/produce")
async def produce_production(
    production_id: str, request: ProduceRequest, current_user: User = Depends(get_current_user)
):
    """Generate media for a planned production (resumes failed / interrupted / cancelled ones)."""
    prod = _get_production(production_id)
    if prod["status"] == "completed":
        raise HTTPException(status_code=409, detail="Production already completed")
    _cost_gate(request.confirm_cost, prod["estimate"])
    try:
        movie_pipeline.start(production_id, produce=True)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return movie_pipeline.load(production_id)


@router.post("/productions/{production_id}/cancel")
async def cancel_production(production_id: str, current_user: User = Depends(get_current_user)):
    _get_production(production_id)
    return movie_pipeline.cancel(production_id)


@router.get("/productions")
async def list_productions(current_user: User = Depends(get_current_user_optional)) -> List[Dict[str, Any]]:
    return movie_pipeline.list_productions()


@router.get("/productions/{production_id}")
async def get_production(production_id: str, current_user: User = Depends(get_current_user_optional)):
    prod = _get_production(production_id)
    prod.pop("script_raw", None)
    return prod


@router.get("/productions/{production_id}/video")
async def production_video(production_id: str):
    prod = _get_production(production_id)
    path = prod.get("video_path")
    if prod["status"] != "completed" or not path or not Path(path).is_file():
        raise HTTPException(status_code=404, detail="No finished video for this production")
    return FileResponse(path, media_type="video/mp4", filename=f"{production_id}.mp4")
