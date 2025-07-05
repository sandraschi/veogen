"""
Video Generation API Endpoints
Uses MCP-based video service for Veo generation
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel

from app.services.video_service import video_service
from app.deps import get_current_user
from app.models.user import User

router = APIRouter()

class VideoGenerationRequest(BaseModel):
    prompt: str
    duration: int = 10
    aspect_ratio: str = "16:9"
    style: str = "cinematic"

class VideoGenerationResponse(BaseModel):
    status: str
    video_id: str
    video_url: Optional[str] = None
    duration: Optional[int] = None
    prompt: Optional[str] = None
    error: Optional[str] = None

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

@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a video using Veo via MCP"""
    try:
        result = await video_service.generate_video(
            prompt=request.prompt,
            user_id=current_user.id,
            duration=request.duration,
            aspect_ratio=request.aspect_ratio,
            style=request.style
        )
        
        return VideoGenerationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@router.get("/status/{video_id}", response_model=VideoStatusResponse)
async def get_video_status(
    video_id: str,
    current_user: User = Depends(get_current_user)
):
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
async def list_user_videos(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get all videos for the current user"""
    try:
        videos = await video_service.get_user_videos(current_user.id, limit)
        return [VideoStatusResponse(**video) for video in videos]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user videos: {str(e)}")

@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    current_user: User = Depends(get_current_user)
):
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