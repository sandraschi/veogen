# Music Generation API Endpoints

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

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

@router.post("/generate", response_model=MusicGenerationResponse)
async def generate_music(
    music_data: MusicGenerationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate music using Google Lyria AI
    
    - **prompt**: Description of the music to generate (5-500 chars)
    - **style**: Music style (classical, jazz, rock, electronic, etc.)
    - **mood**: Music mood (happy, sad, energetic, calm, etc.)
    - **duration**: Music duration in seconds (10-300)
    - **tempo**: Optional BPM (60-200)
    - **musical_key**: Optional musical key (e.g., "C major", "A minor")
    - **vocal_style**: Optional vocal style for songs with lyrics
    - **instruments**: Optional list of preferred instruments
    """
    try:
        music_gen = await music_service.create_music_generation(
            db, music_data, current_user
        )
        
        return MusicGenerationResponse(
            job_id=music_gen.id,
            status=music_gen.status,
            message="Music generation started successfully",
            estimated_completion_time=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start music generation: {str(e)}"
        )

@router.get("/{music_id}", response_model=MusicGeneration)
async def get_music_generation(
    music_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get music generation status and details"""
    music_gen = await music_service.get_music_generation(
        db, music_id, current_user
    )
    
    if not music_gen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music generation not found"
        )
    
    return music_gen

@router.get("/", response_model=List[MusicGeneration])
async def list_music_generations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    style: Optional[MusicStyle] = None,
    mood: Optional[MusicMood] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's music generations with optional filtering"""
    music_gens = await music_service.list_user_music(
        db, current_user, skip=skip, limit=limit,
        style=style, mood=mood, status=status
    )
    return music_gens

@router.delete("/{music_id}")
async def delete_music_generation(
    music_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a music generation"""
    music_gen = await music_service.get_music_generation(
        db, music_id, current_user
    )
    
    if not music_gen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music generation not found"
        )
    
    await music_service.delete_music_generation(db, music_id)
    return {"message": "Music generation deleted successfully"}

@router.post("/{music_id}/regenerate", response_model=MusicGenerationResponse)
async def regenerate_music(
    music_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Regenerate a failed music generation"""
    music_gen = await music_service.get_music_generation(
        db, music_id, current_user
    )
    
    if not music_gen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music generation not found"
        )
    
    if music_gen.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only regenerate failed music generations"
        )
    
    await music_service.regenerate_music(db, music_id)
    
    return MusicGenerationResponse(
        job_id=music_gen.id,
        status="pending",
        message="Music regeneration started"
    )

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
