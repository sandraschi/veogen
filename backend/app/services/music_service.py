# Music Service Layer for Lyria Integration

import asyncio
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.services.music.lyria_service import lyria_service, MusicGenerationRequest
from app.schemas.music import MusicGenerationCreate, MusicGeneration
from app.models.user import User

logger = logging.getLogger(__name__)

class MusicService:
    """Music generation service layer"""
    
    def __init__(self):
        self.lyria = lyria_service
        self.active_generations = {}  # In-memory storage for demo
    
    async def create_music_generation(
        self, 
        db: AsyncSession, 
        music_data: MusicGenerationCreate, 
        user: User
    ) -> MusicGeneration:
        """Create and start a music generation job"""
        
        # Create music generation record
        music_gen = MusicGeneration(
            id=uuid4(),
            user_id=user.id,
            prompt=music_data.prompt,
            style=music_data.style,
            mood=music_data.mood,
            duration=music_data.duration,
            tempo=music_data.tempo,
            musical_key=music_data.musical_key,
            vocal_style=music_data.vocal_style,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        # Store in memory for demo (would be database in production)
        self.active_generations[music_gen.id] = music_gen
        
        # Start background generation
        asyncio.create_task(self._generate_music_async(music_gen))
        
        return music_gen
    
    async def _generate_music_async(self, music_gen: MusicGeneration):
        """Background task to generate music"""
        try:
            # Update status to generating
            music_gen.status = "generating"
            music_gen.updated_at = datetime.utcnow()
            
            # Create Lyria request
            lyria_request = MusicGenerationRequest(
                prompt=music_gen.prompt,
                style=music_gen.style,
                mood=music_gen.mood,
                duration=music_gen.duration,
                tempo=music_gen.tempo,
                key=music_gen.musical_key,
                vocal_style=music_gen.vocal_style.value if music_gen.vocal_style != "none" else None
            )
            
            # Generate music using Lyria
            result = await self.lyria.generate_music(lyria_request)
            
            # Update generation with results
            music_gen.status = "completed"
            music_gen.completed_at = datetime.utcnow()
            music_gen.audio_url = result.audio_url
            music_gen.preview_url = result.preview_url
            music_gen.waveform_data = result.waveform_data
            music_gen.lyrics = result.lyrics
            music_gen.chord_progression = result.chord_progression
            music_gen.generation_time = result.metadata.get("generation_time")
            
        except Exception as e:
            logger.error(f"Music generation failed for {music_gen.id}: {e}")
            music_gen.status = "failed"
            music_gen.error_message = str(e)
            music_gen.updated_at = datetime.utcnow()
    
    async def get_music_generation(
        self, 
        db: AsyncSession, 
        music_id: UUID, 
        user: User
    ) -> Optional[MusicGeneration]:
        """Get music generation by ID"""
        return self.active_generations.get(music_id)
    
    async def list_user_music(
        self,
        db: AsyncSession,
        user: User,
        skip: int = 0,
        limit: int = 20,
        style: Optional[str] = None,
        mood: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[MusicGeneration]:
        """List user's music generations with filtering"""
        user_music = [
            music for music in self.active_generations.values()
            if music.user_id == user.id
        ]
        
        # Apply filters
        if style:
            user_music = [m for m in user_music if m.style == style]
        if mood:
            user_music = [m for m in user_music if m.mood == mood]
        if status:
            user_music = [m for m in user_music if m.status == status]
        
        # Sort by creation date (newest first)
        user_music.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return user_music[skip:skip + limit]
    
    async def delete_music_generation(self, db: AsyncSession, music_id: UUID):
        """Delete music generation"""
        if music_id in self.active_generations:
            del self.active_generations[music_id]
    
    async def regenerate_music(self, db: AsyncSession, music_id: UUID):
        """Regenerate failed music"""
        music_gen = self.active_generations.get(music_id)
        if music_gen:
            music_gen.status = "pending"
            music_gen.error_message = None
            music_gen.updated_at = datetime.utcnow()
            
            # Start regeneration
            asyncio.create_task(self._generate_music_async(music_gen))
    
    async def get_download_url(self, music_gen: MusicGeneration, format: str) -> str:
        """Get download URL for music file"""
        if format == "mp3":
            return music_gen.audio_url
        else:
            # Convert format (would be implemented in production)
            base_url = music_gen.audio_url.replace('.mp3', f'.{format}')
            return base_url
    
    async def create_remix(
        self,
        db: AsyncSession,
        original_music: MusicGeneration,
        remix_style: str,
        remix_mood: Optional[str],
        user: User
    ) -> MusicGeneration:
        """Create a remix of existing music"""
        
        # Create remix generation
        remix_prompt = f"Remix of: {original_music.prompt} in {remix_style} style"
        if remix_mood:
            remix_prompt += f" with {remix_mood} mood"
        
        remix_data = MusicGenerationCreate(
            prompt=remix_prompt,
            style=remix_style,
            mood=remix_mood or original_music.mood,
            duration=original_music.duration,
            tempo=original_music.tempo,
            musical_key=original_music.musical_key,
            vocal_style=original_music.vocal_style
        )
        
        return await self.create_music_generation(db, remix_data, user)

# Global service instance
music_service = MusicService()
