# Image Generation Schemas

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class ImageStyle(str, Enum):
    PHOTOREALISTIC = "photorealistic"
    ARTISTIC = "artistic"
    ILLUSTRATION = "illustration"
    PAINTING = "painting"
    SKETCH = "sketch"
    ANIME = "anime"
    CARTOON = "cartoon"
    ABSTRACT = "abstract"

class ImageQuality(str, Enum):
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"

class AspectRatio(str, Enum):
    SQUARE = "1:1"
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    CLASSIC = "4:3"

class ImageGenerationCreate(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500, description="Image description")
    style: ImageStyle = Field(default=ImageStyle.PHOTOREALISTIC, description="Image style")
    aspect_ratio: AspectRatio = Field(default=AspectRatio.SQUARE, description="Image dimensions")
    quality: ImageQuality = Field(default=ImageQuality.STANDARD, description="Image quality")
    
    class Config:
        json_encoders = {
            ImageStyle: lambda v: v.value,
            ImageQuality: lambda v: v.value,
            AspectRatio: lambda v: v.value,
        }

class ImageGenerationResponse(BaseModel):
    job_id: UUID
    status: str
    message: str
    estimated_completion_time: Optional[datetime] = None

class ImageGeneration(BaseModel):
    id: UUID
    user_id: UUID
    prompt: str
    style: ImageStyle
    aspect_ratio: AspectRatio
    quality: ImageQuality
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error_message: Optional[str] = None
    generation_time: Optional[float] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            ImageStyle: lambda v: v.value,
            ImageQuality: lambda v: v.value,
            AspectRatio: lambda v: v.value,
        }

class ImageVariationCreate(BaseModel):
    original_image_id: UUID
    variation_count: int = Field(default=4, ge=1, le=8)
    
class ImageVariationResponse(BaseModel):
    job_ids: List[UUID]
    status: str
    message: str
