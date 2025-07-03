from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional, List, Dict, Any
import logging
from app.services.gemini_cli import gemini_service
from app.models.video_request import (
    VideoGenerationRequest, 
    VideoGenerationResponse,
    VideoGenerationStatus
)
import uuid
import base64
from PIL import Image
import io
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for job tracking (use Redis in production)
job_tracker = {}

@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a video using Google's Veo model via Gemini CLI
    """
    try:
        job_id = str(uuid.uuid4())
        
        # Store job in tracker
        job_tracker[job_id] = {
            "status": "processing",
            "progress": 0,
            "request": request.dict(),
            "created_at": datetime.now().isoformat()
        }
        
        # Start background task for video generation
        background_tasks.add_task(
            generate_video_background,
            job_id,
            request
        )
        
        return VideoGenerationResponse(
            job_id=job_id,
            status="processing",
            message="Video generation started",
            progress=0
        )
        
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        if job_id in job_tracker:
            job_tracker[job_id]["status"] = "failed"
            job_tracker[job_id]["error"] = str(e)
        
        raise HTTPException(
            status_code=500,
            detail=f"Video generation failed: {str(e)}"
        )

async def generate_video_background(job_id: str, request: VideoGenerationRequest):
    """Background task for video generation"""
    try:
        # Update progress
        job_tracker[job_id]["progress"] = 10
        
        # Generate video using Gemini CLI
        result = await gemini_service.generate_video(
            prompt=request.prompt,
            duration=request.duration,
            aspect_ratio=request.aspect_ratio,
            style=request.style,
            seed=request.seed,
            temperature=request.temperature
        )
        
        # Update job tracker with success
        job_tracker[job_id].update({
            "status": "completed",
            "progress": 100,
            "result": result,
            "completed_at": datetime.now().isoformat()
        })
        
        logger.info(f"Video generation completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Background video generation failed for job {job_id}: {str(e)}")
        job_tracker[job_id].update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })

@router.get("/status/{job_id}", response_model=VideoGenerationStatus)
async def get_generation_status(job_id: str):
    """
    Get the status of a video generation job
    """
    if job_id not in job_tracker:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    job_info = job_tracker[job_id]
    return VideoGenerationStatus(
        job_id=job_id,
        status=job_info["status"],
        progress=job_info["progress"],
        error_message=job_info.get("error")
    )

@router.get("/download/{job_id}")
async def download_video(job_id: str):
    """
    Download the generated video
    """
    if job_id not in job_tracker:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    job_info = job_tracker[job_id]
    
    if job_info["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Video generation not completed"
        )
    
    result = job_info.get("result")
    if not result or "video_data" not in result:
        raise HTTPException(
            status_code=404,
            detail="Video data not found"
        )
    
    video_data = result["video_data"]
    
    def generate_video_stream():
        yield video_data
    
    return StreamingResponse(
        generate_video_stream(),
        media_type="video/mp4",
        headers={
            "Content-Disposition": f"attachment; filename=video_{job_id}.mp4"
        }
    )

@router.post("/upload-reference")
async def upload_reference_image(file: UploadFile = File(...)):
    """
    Upload a reference image for video generation
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Only image files are allowed"
            )
        
        # Read and validate image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "image_base64": image_base64,
            "filename": file.filename,
            "size": len(image_data),
            "dimensions": image.size
        }
        
    except Exception as e:
        logger.error(f"Image upload failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Image upload failed: {str(e)}"
        )

@router.get("/jobs")
async def list_jobs():
    """
    List all generation jobs
    """
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job_info["status"],
                "progress": job_info["progress"],
                "created_at": job_info.get("created_at"),
                "completed_at": job_info.get("completed_at")
            }
            for job_id, job_info in job_tracker.items()
        ]
    }

@router.get("/models")
async def list_available_models():
    """
    List available Veo models
    """
    try:
        models = await gemini_service.list_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return {"models": ["veo-3"]}

@router.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """
    Get information about a specific model
    """
    try:
        info = await gemini_service.get_model_info(model_name)
        return info
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Model information not found: {str(e)}"
        )

@router.post("/setup")
async def setup_gemini_cli():
    """
    Setup and verify Gemini CLI installation
    """
    try:
        success = await gemini_service.install_gemini_cli()
        if success:
            return {"message": "Gemini CLI setup successful"}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to setup Gemini CLI"
            )
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Setup failed: {str(e)}"
        )

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a generation job
    """
    if job_id not in job_tracker:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    del job_tracker[job_id]
    return {"message": "Job deleted successfully"}

@router.get("/health")
async def health_check():
    """
    Health check for video generation service
    """
    try:
        # Check if Gemini CLI is available
        models = await gemini_service.list_available_models()
        return {
            "status": "healthy",
            "gemini_cli_available": len(models) > 0,
            "available_models": models,
            "active_jobs": len([j for j in job_tracker.values() if j["status"] == "processing"])
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "gemini_cli_available": False
        }
