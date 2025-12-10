"""
Video Generation API Router using Gemini CLI Veo integration.
"""

import base64
import io
import logging
import uuid
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.api.api_v1.endpoints import video as video_endpoints
from app.database import User
from app.models.video_request import (
    VideoGenerationRequest,
    VideoGenerationStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["video"])

# In-memory job tracker (lightweight persistence for recent generations)
job_tracker: Dict[str, Dict] = {}

@router.post("/generate", response_model=video_endpoints.VideoGenerateResponse)
async def generate_video(
    request: VideoGenerationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate a video using Gemini CLI Veo integration.
    """
    job_id = str(uuid.uuid4())

    prompt_parts = [request.prompt]
    if request.style:
        prompt_parts.append(f"Style: {request.style}")
    if request.aspect_ratio:
        prompt_parts.append(f"Aspect ratio: {request.aspect_ratio}")
    if request.temperature is not None:
        prompt_parts.append(f"Creativity level: {request.temperature:.2f}")
    if request.negative_prompt:
        prompt_parts.append(f"Avoid: {request.negative_prompt}")
    if request.camera_movement:
        prompt_parts.append(f"Camera movement: {request.camera_movement}")
    if request.motion_intensity:
        prompt_parts.append(f"Motion intensity: {request.motion_intensity}")

    enriched_prompt = ". ".join(prompt_parts)

    try:
        result = await video_endpoints.gemini_service.generate_video(
            prompt=enriched_prompt,
            duration=request.duration or 10,
            aspect_ratio=request.aspect_ratio or "16:9",
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

    api_used = result.get("api_used") or "gemini_cli_mcp"
    metadata = {
        "prompt": request.prompt,
        "style": request.style,
        "duration": str(request.duration),
        "aspect_ratio": request.aspect_ratio,
        "api_used": api_used,
    }

    job_tracker[job_id] = {
        "job_id": job_id,
        "user_id": current_user.id,
        "status": "completed",
        "progress": 100,
        "created_at": datetime.utcnow().isoformat(),
        "result": {
            "video_url": data_url,
            "metadata": metadata,
            "api_used": api_used,
        },
        "message": result.get("message", "Video generated successfully."),
    }

    payload = {
        "status": "success",
        "video": {"url": data_url, "metadata": metadata},
        "message": result.get("message"),
        "api_used": api_used,
    }
    logger.debug("Video generation payload: %s", payload)
    return payload

@router.get("/status/{job_id}", response_model=VideoGenerationStatus)
async def get_generation_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a video generation job from in-memory tracker.
    """
    job_info = job_tracker.get(job_id)
    if not job_info:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_info["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this job")

    result = job_info.get("result")

    return VideoGenerationStatus(
        job_id=job_id,
        status=job_info["status"],
        progress=job_info.get("progress", 0),
        error_message=job_info.get("error"),
        current_step=job_info.get("message"),
        video_url=result.get("video_url") if result else None,
    )

@router.get("/jobs")
async def list_jobs(current_user: User = Depends(get_current_user)):
    """
    List all video generation jobs for the current user
    """
    jobs = [
        {
            "job_id": job["job_id"],
            "status": job["status"],
            "progress": job.get("progress", 0),
            "created_at": job.get("created_at"),
            "completed_at": job.get("completed_at"),
        }
        for job in job_tracker.values()
        if job["user_id"] == current_user.id
    ]

    return {"jobs": jobs, "total": len(jobs)}

@router.get("/download/{job_id}")
async def download_video(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a completed video file
    """
    job_info = job_tracker.get(job_id)
    if not job_info:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_info["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to download this job")

    result = job_info.get("result")
    if not result or "video_url" not in result:
        raise HTTPException(
            status_code=404,
            detail="Video data not available for this job",
        )

    video_url = result["video_url"]
    if not video_url.startswith("data:"):
        raise HTTPException(
            status_code=400,
            detail="Stored video format is unsupported for download",
        )

    header, b64_data = video_url.split(",", 1)
    media_type = header.split(";")[0].split(":")[1] if ":" in header else "video/mp4"
    content = base64.b64decode(b64_data)

    filename = f"veogen-video-{job_id}.mp4"

    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(content)),
        },
    )

@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a video generation job
    """
    job_info = job_tracker.get(job_id)
    if not job_info:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_info["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this job")

    del job_tracker[job_id]

    return {"message": "Job deleted successfully"}

@router.get("/health")
async def health_check():
    """
    Health check for video generation service
    """
    active_jobs = sum(
        1
        for job in job_tracker.values()
        if job.get("status") == "processing"
    )
    return {
        "status": "healthy",
        "mcp_veo_available": True,
        "active_jobs": active_jobs,
    }
