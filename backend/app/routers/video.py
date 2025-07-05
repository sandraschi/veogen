"""
Video Generation API Router
Handles video generation requests using Google's Veo model via MCP
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional, List, Dict, Any
import logging
import uuid
import base64
from PIL import Image
import io
import json
from datetime import datetime

from ..services.video_service import video_service
from ..models.video_request import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoGenerationStatus,
    VideoJobInfo
)
from ..deps import get_current_user
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/video", tags=["video"])

# In-memory job tracker (in production, use Redis or database)
job_tracker = {}

async def generate_video_background(job_id: str, request: VideoGenerationRequest, user_id: int):
    """Background task for video generation with progress tracking"""
    try:
        # Update initial progress
        job_tracker[job_id]["progress"] = 5
        job_tracker[job_id]["status"] = "processing"
        
        # Progress callback function
        def progress_callback(progress: int, status: str = None, message: str = None):
            job_tracker[job_id]["progress"] = progress
            if status:
                job_tracker[job_id]["status"] = status
            if message:
                job_tracker[job_id]["message"] = message
            logger.info(f"Job {job_id} progress: {progress}% - {message}")
        
        # Generate video using enhanced service
        result = await video_service.generate_video(
            prompt=request.prompt,
            duration=request.duration,
            aspect_ratio=request.aspect_ratio,
            style=request.style,
            seed=request.seed,
            temperature=request.temperature,
            user_id=user_id,
            progress_callback=progress_callback
        )
        
        if result["status"] == "success":
            # Update job tracker with success
            job_tracker[job_id].update({
                "status": "completed",
                "progress": 100,
                "result": result,
                "completed_at": result.get("completed_at")
            })
            logger.info(f"Video generation completed for job {job_id}")
        else:
            # Update job tracker with error
            job_tracker[job_id].update({
                "status": "failed",
                "error": result.get("error", "Unknown error"),
                "failed_at": result.get("failed_at")
            })
            logger.error(f"Video generation failed for job {job_id}: {result.get('error')}")
        
    except Exception as e:
        logger.error(f"Background video generation failed for job {job_id}: {str(e)}")
        job_tracker[job_id].update({
            "status": "failed",
            "error": str(e),
            "failed_at": result.get("failed_at") if 'result' in locals() else None
        })

@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a video using Google's Veo model via MCP
    """
    try:
        # Create job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job tracker
        job_tracker[job_id] = {
            "job_id": job_id,
            "user_id": current_user.id,
            "status": "queued",
            "progress": 0,
            "request": request.dict(),
            "created_at": datetime.utcnow().isoformat(),
            "message": "Job queued for processing"
        }
        
        # Add background task
        background_tasks.add_task(
            generate_video_background,
            job_id,
            request,
            current_user.id
        )
        
        logger.info(f"Video generation job {job_id} queued for user {current_user.id}")
        
        return VideoGenerationResponse(
            status="queued",
            job_id=job_id,
            message="Video generation job queued successfully"
        )
        
    except Exception as e:
        logger.error(f"Error queuing video generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue video generation: {str(e)}"
        )

@router.get("/status/{job_id}", response_model=VideoGenerationStatus)
async def get_generation_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a video generation job
    """
    try:
        # First check in-memory tracker
        if job_id in job_tracker:
            job_info = job_tracker[job_id]
            
            # Check authorization
            if job_info["user_id"] != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to view this job"
                )
            
            return VideoGenerationStatus(
                job_id=job_id,
                status=job_info["status"],
                progress=job_info["progress"],
                error_message=job_info.get("error"),
                current_step=job_info.get("message"),
                video_url=job_info.get("result", {}).get("video_url") if job_info.get("result") else None
            )
        
        # Fallback to MCP service
        job_status = await video_service.get_generation_status(job_id, current_user.id)
        
        if job_status["status"] == "not_found":
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )
        elif job_status["status"] == "unauthorized":
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view this job"
            )
        elif job_status["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving job status: {job_status['error']}"
            )
        
        return VideoGenerationStatus(
            job_id=job_id,
            status=job_status["status"],
            progress=job_status["progress"],
            error_message=job_status.get("error_message"),
            current_step=job_status.get("message"),
            video_url=job_status.get("result", {}).get("video_url") if job_status.get("result") else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting generation status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )

@router.get("/jobs")
async def list_jobs(current_user: User = Depends(get_current_user)):
    """
    List all video generation jobs for the current user
    """
    try:
        # Get jobs from MCP service
        result = await video_service.list_user_jobs(current_user.id)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Error listing jobs: {result['error']}"
            )
        
        # Combine with in-memory jobs
        mcp_jobs = result["jobs"]
        memory_jobs = [
            {
                "job_id": job["job_id"],
                "status": job["status"],
                "progress": job["progress"],
                "created_at": job["created_at"],
                "completed_at": job.get("completed_at")
            }
            for job in job_tracker.values()
            if job["user_id"] == current_user.id
        ]
        
        # Merge and deduplicate
        all_jobs = {}
        for job in mcp_jobs + memory_jobs:
            if job["job_id"] not in all_jobs:
                all_jobs[job["job_id"]] = job
            else:
                # Prefer memory job if it has more recent info
                existing = all_jobs[job["job_id"]]
                if job.get("progress", 0) > existing.get("progress", 0):
                    all_jobs[job["job_id"]] = job
        
        return {
            "jobs": list(all_jobs.values()),
            "total": len(all_jobs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list jobs: {str(e)}"
        )

@router.get("/download/{job_id}")
async def download_video(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a completed video file
    """
    try:
        # Try to download from MCP service
        file_data = await video_service.download_video(job_id, current_user.id)
        
        if not file_data:
            raise HTTPException(
                status_code=404,
                detail="Video file not found or not completed"
            )
        
        # Create streaming response
        return StreamingResponse(
            io.BytesIO(file_data["content"]),
            media_type=file_data["content_type"],
            headers={
                "Content-Disposition": f"attachment; filename={file_data['filename']}",
                "Content-Length": str(file_data["size"])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download video: {str(e)}"
        )

@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a video generation job
    """
    try:
        result = await video_service.delete_job(job_id, current_user.id)
        
        if result["status"] == "not_found":
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )
        elif result["status"] == "unauthorized":
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this job"
            )
        elif result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting job: {result['error']}"
            )
        
        # Also remove from memory tracker
        if job_id in job_tracker:
            del job_tracker[job_id]
        
        return {"message": "Job deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete job: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check for video generation service
    """
    try:
        health_status = await video_service.get_health_status()
        
        return {
            "status": health_status["status"],
            "mcp_veo_available": health_status["mcp_veo_available"],
            "active_jobs": health_status["active_jobs"],
            "error": health_status.get("error")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "mcp_veo_available": False,
            "active_jobs": 0
        }
