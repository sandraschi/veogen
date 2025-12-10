"""
Music Generation API Endpoints backed by Gemini CLI Lyria calls.
"""

import base64
import logging
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.music import (
    MusicGenerationResponse,
    MusicMood,
    MusicStyle,
)
from app.services.gemini_cli import gemini_service
from app.services.music_service import music_service

logger = logging.getLogger(__name__)

router = APIRouter()


class MusicGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Describe the music to generate")
    duration: int = Field(30, ge=5, le=180, description="Length of track in seconds")
    genre: str = Field("electronic", description="High-level genre label")
    mood: Optional[str] = Field(None, description="Desired mood (e.g. uplifting, calm)")
    tempo: Optional[int] = Field(None, ge=40, le=200, description="Target tempo in BPM")
    creativity: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Creativity hint relayed in prompt"
    )
    instruments: Optional[str] = Field(
        None, description="Comma separated instruments to highlight"
    )

class SpeechGenerationRequest(BaseModel):
    text: str
    voice: str = "en-US-Neural2-F"

class GeneratedTrack(BaseModel):
    url: str
    metadata: Dict[str, Optional[str]]


class MusicGenerateResponse(BaseModel):
    status: str
    track: GeneratedTrack
    message: Optional[str] = None
    api_used: Optional[str] = None

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

@router.post("/generate", response_model=MusicGenerateResponse)
async def generate_music(
    request: MusicGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate music using Gemini CLI Lyria support."""
    prompt_parts = [request.prompt]

    if request.genre:
        prompt_parts.append(f"Genre: {request.genre}")
    if request.mood:
        prompt_parts.append(f"Mood: {request.mood}")
    if request.tempo:
        prompt_parts.append(f"Tempo: {request.tempo} BPM")
    if request.instruments:
        prompt_parts.append(f"Instruments: {request.instruments}")
    if request.creativity is not None:
        prompt_parts.append(
            f"Creativity level target: {request.creativity:.2f} (0 structured, 1 experimental)"
        )

    enriched_prompt = ". ".join(prompt_parts)

    try:
        result = await gemini_service.generate_music(
            prompt=enriched_prompt,
            duration=request.duration,
            style=request.genre,
            db_session=None,
            user_id=str(current_user.id),
        )
    except Exception as exc:
        logger.error("Gemini music generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Music generation failed due to upstream error.",
        ) from exc

    if result.get("status") != "success":
        message = result.get("message") or "Music generation failed."
        logger.error("Gemini returned error for music generation: %s", message)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)

    music_bytes = result.get("music_data", b"")
    if not music_bytes:
        logger.error("No music data returned from Gemini.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Music generation did not return audio data.",
        )

    data_url = "data:audio/mpeg;base64," + base64.b64encode(music_bytes).decode("ascii")

    metadata = {
        "prompt": request.prompt,
        "genre": request.genre,
        "mood": request.mood,
        "duration": str(request.duration),
        "tempo": str(request.tempo) if request.tempo else None,
        "instruments": request.instruments,
        "api_used": result.get("api_used"),
    }

    return MusicGenerateResponse(
        status="success",
        track=GeneratedTrack(url=data_url, metadata=metadata),
        message=result.get("message"),
        api_used=result.get("api_used"),
    )

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
async def get_available_voices(current_user: User = Depends(get_current_user)):
    """Get list of available Chirp voices"""
    try:
        voices = await music_service.get_available_voices(current_user.id)
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
