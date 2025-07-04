# Music Generation Schemas

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class MusicStyle(str, Enum):
    POP = "pop"
    ROCK = "rock"
    ELECTRONIC = "electronic"
    CLASSICAL = "classical"
    JAZZ = "jazz"
    AMBIENT = "ambient"
    CINEMATIC = "cinematic"
    FOLK = "folk"
    BLUES = "blues"
    COUNTRY = "country"
    HIP_HOP = "hip_hop"
    REGGAE = "reggae"

class MusicMood(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    ENERGETIC = "energetic"
    CALM = "calm"
    MYSTERIOUS = "mysterious"
    ROMANTIC = "romantic"
    EPIC = "epic"
    NOSTALGIC = "nostalgic"

class VocalStyle(str, Enum):
    NONE = "none"
    MALE = "male"
    FEMALE = "female"
    CHOIR = "choir"
    HUMMING = "humming"

class MusicGenerationCreate(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500, description="Music description")
    style: MusicStyle = Field(default=MusicStyle.POP, description="Music style")
    mood: MusicMood = Field(default=MusicMood.HAPPY, description="Music mood")
    duration: int = Field(default=30, ge=10, le=300, description="Duration in seconds")
    tempo: Optional[int] = Field(default=120, ge=60, le=200, description="Tempo in BPM")
    musical_key: Optional[str] = Field(default="C major", description="Musical key")
    vocal_style: VocalStyle = Field(default=VocalStyle.NONE, description="Vocal style")
    
    class Config:
        json_encoders = {
            MusicStyle: lambda v: v.value,
            MusicMood: lambda v: v.value,
            VocalStyle: lambda v: v.value,
        }

class MusicGenerationResponse(BaseModel):
    job_id: UUID
    status: str
    message: str
    estimated_completion_time: Optional[datetime] = None

class MusicGeneration(BaseModel):
    id: UUID
    user_id: UUID
    prompt: str
    style: MusicStyle
    mood: MusicMood
    duration: int
    tempo: Optional[int] = None
    musical_key: Optional[str] = None
    vocal_style: VocalStyle
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    audio_url: Optional[str] = None
    preview_url: Optional[str] = None
    waveform_data: Optional[List[float]] = None
    lyrics: Optional[str] = None
    chord_progression: Optional[List[str]] = None
    error_message: Optional[str] = None
    generation_time: Optional[float] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            MusicStyle: lambda v: v.value,
            MusicMood: lambda v: v.value,
            VocalStyle: lambda v: v.value,
        }

class MusicRemixCreate(BaseModel):
    original_music_id: UUID
    new_style: MusicStyle
    new_mood: Optional[MusicMood] = None
    
class MusicRemixResponse(BaseModel):
    job_id: UUID
    status: str
    message: str
