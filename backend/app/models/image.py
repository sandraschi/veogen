# Image Generation Database Models

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class ImageGeneration(Base):
    """Image generation database model"""

    __tablename__ = "image_generations"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Generation parameters
    prompt = Column(Text, nullable=False)
    style = Column(String(50), nullable=False, index=True)
    aspect_ratio = Column(String(20), default="16:9")
    resolution = Column(String(20), default="1024x1024")
    seed = Column(Integer)
    guidance_scale = Column(Float, default=7.5)
    num_inference_steps = Column(Integer, default=50)

    # Generation status
    status = Column(String(20), default="pending", nullable=False, index=True)  # pending, processing, completed, failed

    # Results
    image_url = Column(String(500))
    thumbnail_url = Column(String(500))

    # Image metadata
    width = Column(Integer)
    height = Column(Integer)
    file_size_bytes = Column(Integer)
    format = Column(String(10))  # jpg, png, webp

    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)

    # Additional metadata
    generation_metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="image_generations")
