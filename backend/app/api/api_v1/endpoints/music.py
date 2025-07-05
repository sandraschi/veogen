"""
Music Generation API Endpoints
Uses MCP-based music service for Lyria generation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.music import (
    MusicGeneration,
    MusicGenerationCreate,
    MusicGenerationResponse,
    MusicStyle,
    MusicMood
)
from app.services.music_service import music_service

router = APIRouter()

class MusicGenerationRequest(BaseModel):
    prompt: str
    duration: int = 30
    style: str = "electronic"

class SpeechGenerationRequest(BaseModel):
    text: str
    voice: str = "en-US-Neural2-F"

class MusicGenerationResponse(BaseModel):
    status: str
    music_id: str
    music_url: Optional[str] = None
    duration: Optional[int] = None
    prompt: Optional[str] = None
    error: Optional[str] = None

class SpeechGenerationResponse(BaseModel):
    status: str
    speech_id: str
    audio_data: Optional[str] = None
    voice: Optional[str] = None
    text: Optional[str] = None
    error: Optional[str] = None

class MusicStatusResponse(BaseModel):
    music_id: str
    status: str
    prompt: str
    duration: int
    style: str
    music_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

@router.post("/generate", response_model=MusicGenerationResponse)
async def generate_music(
    request: MusicGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate music using Lyria via MCP"""
    try:
        result = await music_service.generate_music(
            prompt=request.prompt,
            user_id=current_user.id,
            duration=request.duration,
            style=request.style
        )
        
        return MusicGenerationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Music generation failed: {str(e)}")

@router.post("/speech", response_model=SpeechGenerationResponse)
async def generate_speech(
    request: SpeechGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate speech using Chirp 3 HD via MCP"""
    try:
        result = await music_service.generate_speech(
            text=request.text,
            user_id=current_user.id,
            voice=request.voice
        )
        
        return SpeechGenerationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech generation failed: {str(e)}")

@router.get("/status/{music_id}", response_model=MusicStatusResponse)
async def get_music_status(
    music_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the status of a music generation"""
    try:
        result = await music_service.get_music_status(music_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Music not found")
            
        return MusicStatusResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get music status: {str(e)}")

@router.get("/list", response_model=List[MusicStatusResponse])
async def list_user_music(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get all music for the current user"""
    try:
        music_list = await music_service.get_user_music(current_user.id, limit)
        return [MusicStatusResponse(**music) for music in music_list]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user music: {str(e)}")

@router.get("/voices")
async def get_available_voices():
    """Get list of available Chirp voices"""
    try:
        voices = await music_service.get_available_voices()
        return {"voices": voices}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voices: {str(e)}")

@router.delete("/{music_id}")
async def delete_music(
    music_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a music generation"""
    try:
        success = await music_service.delete_music(music_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Music not found")
            
        return {"message": "Music deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete music: {str(e)}")

@router.get("/styles/", response_model=List[str])
async def get_music_styles():
    """Get available music styles"""
    return [style.value for style in MusicStyle]

@router.get("/moods/", response_model=List[str])
async def get_music_moods():
    """Get available music moods"""
    return [mood.value for mood in MusicMood]

@router.get("/{music_id}/download")
async def download_music(
    music_id: UUID,
    format: str = Query("mp3", regex="^(mp3|wav|flac)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download generated music in specified format"""
    music_gen = await music_service.get_music_generation(
        db, music_id, current_user
    )
    
    if not music_gen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music generation not found"
        )
    
    if music_gen.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Music generation not completed"
        )
    
    download_url = await music_service.get_download_url(music_gen, format)
    
    return {"download_url": download_url}

@router.post("/{music_id}/remix", response_model=MusicGenerationResponse)
async def remix_music(
    music_id: UUID,
    remix_style: MusicStyle,
    remix_mood: Optional[MusicMood] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a remix of existing music with different style/mood"""
    original_music = await music_service.get_music_generation(
        db, music_id, current_user
    )
    
    if not original_music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original music not found"
        )
    
    if original_music.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original music must be completed before remixing"
        )
    
    remix = await music_service.create_remix(
        db, original_music, remix_style, remix_mood, current_user
    )
    
    return MusicGenerationResponse(
        job_id=remix.id,
        status=remix.status,
        message="Music remix started successfully"
    )
