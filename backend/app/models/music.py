# Music Generation Database Models and API

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class MusicGeneration(BaseModel):
    """Music generation model"""
    __tablename__ = "music_generations"
    
    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Generation parameters
    prompt = Column(Text, nullable=False)
    style = Column(String(50), nullable=False, index=True)
    mood = Column(String(50), nullable=False, index=True)
    duration = Column(Integer, default=30)  # seconds
    tempo = Column(Integer)  # BPM
    musical_key = Column(String(20))  # Musical key
    vocal_style = Column(String(50))
    
    # Generation status
    status = Column(
        String(20), 
        default="pending", 
        nullable=False,
        index=True
    )  # pending, processing, completed, failed
    
    # Results
    audio_url = Column(String(500))
    preview_url = Column(String(500))
    sheet_music_url = Column(String(500))
    
    # Musical content
    lyrics = Column(Text)
    chord_progression = Column(JSON)
    instruments = Column(JSON)
    waveform_data = Column(JSON)
    
    # Metadata
    generation_time_seconds = Column(Float)
    file_size_bytes = Column(Integer)
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Additional metadata
    metadata = Column(JSONB)
    
    # Relationships
    user = relationship("User", back_populates="music_generations")

# Add to User model
# music_generations = relationship(
#     "MusicGeneration", 
#     back_populates="user",
#     cascade="all, delete-orphan"
# )
