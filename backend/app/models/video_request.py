from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class VideoStyle(str, Enum):
    CINEMATIC = "cinematic"
    REALISTIC = "realistic"
    ANIMATED = "animated"
    ARTISTIC = "artistic"
    DOCUMENTARY = "documentary"
    COMMERCIAL = "commercial"
    ABSTRACT = "abstract"
    VINTAGE = "vintage"
    MODERN = "modern"

class AspectRatio(str, Enum):
    SQUARE = "1:1"
    PORTRAIT = "9:16"
    LANDSCAPE = "16:9"
    WIDESCREEN = "21:9"

class Resolution(str, Enum):
    HD = "720p"
    FHD = "1080p"
    QHD = "1440p"
    UHD = "4K"

class MotionIntensity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CameraMovement(str, Enum):
    STATIC = "static"
    PAN = "pan"
    TILT = "tilt"
    ZOOM = "zoom"
    TRACKING = "tracking"
    HANDHELD = "handheld"
    DRONE = "drone"
    CRANE = "crane"

class VideoGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text description of the video to generate", min_length=10, max_length=2000)
    style: Optional[VideoStyle] = Field(VideoStyle.CINEMATIC, description="Visual style of the video")
    aspect_ratio: Optional[AspectRatio] = Field(AspectRatio.LANDSCAPE, description="Aspect ratio of the video")
    duration: Optional[int] = Field(5, ge=1, le=60, description="Duration in seconds")
    fps: Optional[int] = Field(24, ge=12, le=60, description="Frames per second")
    resolution: Optional[Resolution] = Field(Resolution.FHD, description="Video resolution")
    motion_intensity: Optional[MotionIntensity] = Field(MotionIntensity.MEDIUM, description="Intensity of motion")
    camera_movement: Optional[CameraMovement] = Field(CameraMovement.STATIC, description="Camera movement type")
    reference_image: Optional[str] = Field(None, description="Base64 encoded reference image")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Creativity level")
    negative_prompt: Optional[str] = Field(None, description="What to avoid in the video")
    tags: Optional[List[str]] = Field(None, description="Additional tags for the video")
    
    class Config:
        use_enum_values = True

class VideoGenerationResponse(BaseModel):
    video_url: Optional[str] = Field(None, description="URL of the generated video")
    status: str = Field(..., description="Generation status")
    job_id: Optional[str] = Field(None, description="Job ID for tracking")
    generation_time: Optional[float] = Field(None, description="Time taken to generate")
    enhanced_prompt: Optional[str] = Field(None, description="AI-enhanced prompt used")
    parameters: Optional[dict] = Field(None, description="Parameters used for generation")
    created_at: datetime = Field(default_factory=datetime.now)
    message: Optional[str] = Field(None, description="Status message")
    progress: Optional[int] = Field(0, description="Generation progress percentage")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    
class VideoGenerationStatus(BaseModel):
    job_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    current_step: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class VideoJobInfo(BaseModel):
    job_id: str
    status: str
    progress: int
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    request_data: Optional[dict] = None
    result_data: Optional[dict] = None

class ModelInfo(BaseModel):
    name: str
    description: str
    max_duration: int
    supported_formats: List[str]
    supported_ratios: List[str]
    features: Optional[List[str]] = None
    
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
