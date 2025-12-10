"""
Sound design endpoints for AudioFX.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.config import settings
from app.services.audiofx_service import audiofx_service

router = APIRouter()


class SoundDesignRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=2000)
    duration_seconds: int = Field(15, ge=5, le=60)
    category: str = Field("ambience")
    loop: bool = False
    bpm: int = Field(100, ge=40, le=200)
    intensity: str = Field("medium")


@router.post("/generate")
async def generate_sound_effect(
    payload: SoundDesignRequest,
    current_user=Depends(get_current_user),
):
    if not settings.AUDIOFX_ENABLED:
        raise HTTPException(status_code=503, detail="AudioFX disabled")
    result = await audiofx_service.generate_effect(
        prompt=payload.prompt,
        duration_seconds=payload.duration_seconds,
        category=payload.category,
        loop=payload.loop,
        bpm=payload.bpm,
        intensity=payload.intensity,
    )
    return result

