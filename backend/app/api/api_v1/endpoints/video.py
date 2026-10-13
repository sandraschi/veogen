"""
Video Generation API Endpoints backed by Gemini CLI Veo calls.
"""

import base64
import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.database import User
from app.services.gemini_cli import gemini_service
from app.services.video_service import video_service

logger = logging.getLogger(__name__)

router = APIRouter()


class VideoGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Describe the video to generate")
    duration: int = Field(10, ge=5, le=60, description="Duration in seconds (5-60)")
    aspect_ratio: str = Field("16:9", description="Desired aspect ratio")
    style: str = Field("cinematic", description="Stylistic direction")
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description="Creativity level hint for prompt")
    seed: Optional[int] = Field(None, description="Optional seed for reproducibility")
    negative_prompt: Optional[str] = Field(None, description="Elements that must NOT appear in the video")


class GeneratedVideo(BaseModel):
    url: str
    metadata: Dict[str, Optional[str]]


class VideoGenerateResponse(BaseModel):
    status: str
    video: GeneratedVideo
    message: Optional[str] = None
    api_used: Optional[str] = None


class VideoStatusResponse(BaseModel):
    video_id: str
    status: str
    prompt: str
    duration: int
    aspect_ratio: str
    style: str
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


@router.post("/generate", response_model=VideoGenerateResponse)
async def generate_video(request: VideoGenerationRequest, current_user: User = Depends(get_current_user)):
    """Generate a video using Gemini CLI Veo support."""
    prompt_parts = [request.prompt]
    prompt_parts.append(f"Style: {request.style}")
    prompt_parts.append(f"Aspect ratio: {request.aspect_ratio}")
    if request.temperature is not None:
        prompt_parts.append(f"Creativity level: {request.temperature:.2f}")
    if request.negative_prompt:
        prompt_parts.append(f"Avoid: {request.negative_prompt}")
    if request.seed is not None:
        prompt_parts.append(f"Seed value: {request.seed}")

    enriched_prompt = ". ".join(prompt_parts)

    try:
        result = await gemini_service.generate_video(
            prompt=enriched_prompt,
            duration=request.duration,
            aspect_ratio=request.aspect_ratio,
            style=request.style,
            seed=request.seed,
            temperature=request.temperature or 0.7,
            db_session=None,
            user_id=str(current_user.id),
        )
    except Exception as exc:
        logger.error("Gemini video generation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Video generation failed due to upstream error.",
        ) from exc

    if result.get("status") != "success":
        message = result.get("message") or "Video generation failed."
        logger.error("Gemini returned error for video generation: %s", message)
        raise HTTPException(status_code=500, detail=message)

    video_bytes = result.get("video_data", b"")
    if not video_bytes:
        logger.error("No video data returned from Gemini.")
        raise HTTPException(
            status_code=500,
            detail="Video generation did not return video data.",
        )

    data_url = "data:video/mp4;base64," + base64.b64encode(video_bytes).decode("ascii")

    metadata = {
        "prompt": request.prompt,
        "style": request.style,
        "duration": str(request.duration),
        "aspect_ratio": request.aspect_ratio,
        "api_used": result.get("api_used"),
    }

    return VideoGenerateResponse(
        status="success",
        video=GeneratedVideo(url=data_url, metadata=metadata),
        message=result.get("message"),
        api_used=result.get("api_used"),
    )


@router.get("/status/{video_id}", response_model=VideoStatusResponse)
async def get_video_status(video_id: str, current_user: User = Depends(get_current_user)):
    """Get the status of a video generation"""
    try:
        result = await video_service.get_video_status(video_id)

        if not result:
            raise HTTPException(status_code=404, detail="Video not found")

        return VideoStatusResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get video status: {str(e)}")


@router.get("/list", response_model=List[VideoStatusResponse])
async def list_user_videos(limit: int = 50, current_user: User = Depends(get_current_user)):
    """Get all videos for the current user"""
    try:
        videos = await video_service.get_user_videos(current_user.id, limit)
        return [VideoStatusResponse(**video) for video in videos]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user videos: {str(e)}")


@router.delete("/{video_id}")
async def delete_video(video_id: str, current_user: User = Depends(get_current_user)):
    """Delete a video generation"""
    try:
        success = await video_service.delete_video(video_id, current_user.id)

        if not success:
            raise HTTPException(status_code=404, detail="Video not found")

        return {"message": "Video deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete video: {str(e)}")
