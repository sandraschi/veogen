"""
Music Generation Service for VeoGen
Uses Google's MCP servers for Lyria music generation
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from .mcp_media_service import mcp_media_service
from ..models.music import MusicGeneration
from ..database import get_db

logger = logging.getLogger(__name__)

class MusicService:
    """Service for music generation using Google's Lyria via MCP"""
    
    def __init__(self):
        self.db = get_db()
        
    async def generate_music(self, prompt: str, user_id: int, duration: int = 30, 
                           style: str = "electronic") -> Dict[str, Any]:
        """Generate music using Lyria via MCP servers"""
        
        # Create music generation record
        music_id = str(uuid.uuid4())
        music_generation = MusicGeneration(
            id=music_id,
            user_id=user_id,
            prompt=prompt,
            status="processing",
            duration=duration,
            style=style,
            created_at=datetime.utcnow()
        )
        
        try:
            # Add to database
            self.db.add(music_generation)
            self.db.commit()
            
            logger.info(f"Starting music generation {music_id} for user {user_id}")
            
            # Generate music using MCP service
            result = await mcp_media_service.generate_music(
                prompt=prompt,
                duration=duration,
                user_id=user_id
            )
            
            if result["status"] == "success":
                # Update database with success
                music_generation.status = "completed"
                music_generation.music_url = result["music_url"]
                music_generation.completed_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Music generation {music_id} completed successfully")
                
                return {
                    "status": "success",
                    "music_id": music_id,
                    "music_url": result["music_url"],
                    "duration": result["duration"],
                    "prompt": result["prompt"]
                }
            else:
                # Update database with error
                music_generation.status = "failed"
                music_generation.error_message = result.get("error", "Unknown error")
                music_generation.completed_at = datetime.utcnow()
                self.db.commit()
                
                logger.error(f"Music generation {music_id} failed: {result.get('error')}")
                
                return {
                    "status": "error",
                    "music_id": music_id,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            # Update database with error
            music_generation.status = "failed"
            music_generation.error_message = str(e)
            music_generation.completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.error(f"Music generation {music_id} failed with exception: {e}")
            
            return {
                "status": "error",
                "music_id": music_id,
                "error": str(e)
            }
            
    async def generate_speech(self, text: str, user_id: int, voice: str = "en-US-Neural2-F") -> Dict[str, Any]:
        """Generate speech using Chirp 3 HD via MCP"""
        
        # Create speech generation record
        speech_id = str(uuid.uuid4())
        speech_generation = MusicGeneration(
            id=speech_id,
            user_id=user_id,
            prompt=text,
            status="processing",
            duration=len(text.split()) * 0.5,  # Rough estimate
            style="speech",
            created_at=datetime.utcnow()
        )
        
        try:
            # Add to database
            self.db.add(speech_generation)
            self.db.commit()
            
            logger.info(f"Starting speech generation {speech_id} for user {user_id}")
            
            # Generate speech using MCP service
            result = await mcp_media_service.generate_speech(
                text=text,
                voice=voice,
                user_id=user_id
            )
            
            if result["status"] == "success":
                # Update database with success
                speech_generation.status = "completed"
                speech_generation.music_url = result.get("audio_url")  # Reuse field
                speech_generation.completed_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Speech generation {speech_id} completed successfully")
                
                return {
                    "status": "success",
                    "speech_id": speech_id,
                    "audio_data": result["audio_data"],
                    "voice": result["voice"],
                    "text": result["text"]
                }
            else:
                # Update database with error
                speech_generation.status = "failed"
                speech_generation.error_message = result.get("error", "Unknown error")
                speech_generation.completed_at = datetime.utcnow()
                self.db.commit()
                
                logger.error(f"Speech generation {speech_id} failed: {result.get('error')}")
                
                return {
                    "status": "error",
                    "speech_id": speech_id,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            # Update database with error
            speech_generation.status = "failed"
            speech_generation.error_message = str(e)
            speech_generation.completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.error(f"Speech generation {speech_id} failed with exception: {e}")
            
            return {
                "status": "error",
                "speech_id": speech_id,
                "error": str(e)
            }
            
    async def get_music_status(self, music_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a music generation"""
        try:
            music = self.db.query(MusicGeneration).filter(MusicGeneration.id == music_id).first()
            
            if not music:
                return None
                
            return {
                "music_id": music.id,
                "status": music.status,
                "prompt": music.prompt,
                "duration": music.duration,
                "style": music.style,
                "music_url": music.music_url,
                "error_message": music.error_message,
                "created_at": music.created_at.isoformat() if music.created_at else None,
                "completed_at": music.completed_at.isoformat() if music.completed_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting music status {music_id}: {e}")
            return None
            
    async def get_user_music(self, user_id: int, limit: int = 50) -> list:
        """Get all music for a user"""
        try:
            music_list = self.db.query(MusicGeneration)\
                .filter(MusicGeneration.user_id == user_id)\
                .order_by(MusicGeneration.created_at.desc())\
                .limit(limit)\
                .all()
                
            return [
                {
                    "music_id": music.id,
                    "status": music.status,
                    "prompt": music.prompt,
                    "duration": music.duration,
                    "style": music.style,
                    "music_url": music.music_url,
                    "error_message": music.error_message,
                    "created_at": music.created_at.isoformat() if music.created_at else None,
                    "completed_at": music.completed_at.isoformat() if music.completed_at else None
                }
                for music in music_list
            ]
            
        except Exception as e:
            logger.error(f"Error getting music for user {user_id}: {e}")
            return []
            
    async def get_available_voices(self) -> List[str]:
        """Get list of available Chirp voices"""
        try:
            return await mcp_media_service.get_available_voices(user_id)
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []
            
    async def delete_music(self, music_id: str, user_id: int) -> bool:
        """Delete a music generation record"""
        try:
            music = self.db.query(MusicGeneration)\
                .filter(MusicGeneration.id == music_id, MusicGeneration.user_id == user_id)\
                .first()
                
            if not music:
                return False
                
            self.db.delete(music)
            self.db.commit()
            
            logger.info(f"Deleted music {music_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting music {music_id}: {e}")
            return False

# Global instance
music_service = MusicService()
