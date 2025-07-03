from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class MovieStyle(str, Enum):
    ANIME = "anime"
    PIXAR = "pixar"
    WES_ANDERSON = "wes-anderson"
    CLAYMATION = "claymation"
    SVANKMAJER = "svankmajer"
    ADVERTISEMENT = "advertisement"
    MUSIC_VIDEO = "music-video"
    CINEMATIC = "cinematic"
    DOCUMENTARY = "documentary"

class MoviePreset(str, Enum):
    COMMERCIAL = "commercial"
    SHORT_FILM = "short-film"
    MUSIC_VIDEO = "music-video"
    STORY = "story"
    FEATURE = "feature"

class MovieStatus(str, Enum):
    CREATED = "created"
    SCRIPT_GENERATION = "script_generation"
    SCRIPT_READY = "script_ready"
    SCRIPT_FAILED = "script_failed"
    PRODUCTION = "production"
    COMPLETED = "completed"
    FAILED = "failed"

class MovieProjectRequest(BaseModel):
    title: str = Field(..., description="Movie title", min_length=3, max_length=100)
    concept: str = Field(..., description="Movie concept or plot", min_length=20, max_length=1000)
    style: MovieStyle = Field(..., description="Visual style for the movie")
    preset: MoviePreset = Field(..., description="Movie length preset")
    max_clips: int = Field(10, description="Maximum number of clips/scenes", ge=3, le=50)
    budget: float = Field(5.0, description="Budget limit in USD", ge=1.0, le=100.0)
    auto_generate_script: bool = Field(True, description="Automatically generate script after project creation")
    
    class Config:
        use_enum_values = True

class MovieProjectResponse(BaseModel):
    project_id: str = Field(..., description="Unique project identifier")
    title: str = Field(..., description="Movie title")
    status: str = Field(..., description="Current project status")
    progress: int = Field(0, description="Progress percentage", ge=0, le=100)
    created_at: str = Field(..., description="Creation timestamp")
    estimated_cost: float = Field(0.0, description="Estimated production cost")

class ScriptUpdateRequest(BaseModel):
    script_content: str = Field(..., description="Updated script content", min_length=50)

class SceneInfo(BaseModel):
    id: int = Field(..., description="Scene number")
    title: str = Field(..., description="Scene title")
    duration: int = Field(8, description="Scene duration in seconds")
    description: str = Field(..., description="Scene description")
    visual_prompt: str = Field(..., description="Visual prompt for AI generation")
    continuity_notes: str = Field("", description="Notes about scene continuity")
    status: str = Field("pending", description="Scene status")

class MovieStatusResponse(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    title: str = Field(..., description="Movie title")
    status: str = Field(..., description="Current status")
    progress: int = Field(0, description="Progress percentage", ge=0, le=100)
    scenes_total: int = Field(0, description="Total number of scenes")
    scenes_completed: int = Field(0, description="Number of completed scenes")
    estimated_cost: float = Field(0.0, description="Estimated cost")
    created_at: str = Field(..., description="Creation timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    current_step: Optional[str] = Field(None, description="Current production step")

class MovieScriptResponse(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    title: str = Field(..., description="Movie title")
    script: Optional[str] = Field(None, description="Generated script content")
    scenes: List[SceneInfo] = Field([], description="List of scenes")
    status: str = Field(..., description="Script status")

class MovieProjectInfo(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    title: str = Field(..., description="Movie title")
    status: str = Field(..., description="Current status")
    progress: int = Field(0, description="Progress percentage")
    created_at: str = Field(..., description="Creation timestamp")
    style: str = Field(..., description="Visual style")
    preset: str = Field(..., description="Movie preset")
    scenes_count: int = Field(0, description="Number of scenes")

class StyleInfo(BaseModel):
    id: str = Field(..., description="Style identifier")
    name: str = Field(..., description="Display name with emoji")
    description: str = Field(..., description="Style description")

class PresetInfo(BaseModel):
    id: str = Field(..., description="Preset identifier")
    name: str = Field(..., description="Display name with emoji")
    clips: str = Field(..., description="Number of clips range")
    duration: str = Field(..., description="Duration range")
    cost: str = Field(..., description="Cost estimate range")
    description: str = Field(..., description="Preset description")

class MovieHealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    service: str = Field("movie_maker", description="Service name")
    active_projects: int = Field(0, description="Number of active projects")
    ffmpeg_available: bool = Field(True, description="FFmpeg availability")
    features: List[str] = Field([], description="Available features")
    error: Optional[str] = Field(None, description="Error message if unhealthy")

class ContinuityInfo(BaseModel):
    scene_id: int = Field(..., description="Scene identifier")
    previous_frame: Optional[str] = Field(None, description="Path to previous scene's final frame")
    style_applied: bool = Field(False, description="Whether style transfer was applied")
    transition_type: str = Field("fade", description="Type of transition to use")

class ProductionStep(BaseModel):
    step_name: str = Field(..., description="Name of the production step")
    status: str = Field(..., description="Step status")
    progress: int = Field(0, description="Step progress percentage")
    estimated_time: Optional[int] = Field(None, description="Estimated time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")

class MovieProductionStatus(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    current_step: str = Field(..., description="Current production step")
    overall_progress: int = Field(0, description="Overall progress percentage")
    steps: List[ProductionStep] = Field([], description="Production steps")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    current_scene: Optional[int] = Field(None, description="Currently processing scene")

class MovieCostBreakdown(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    scenes_count: int = Field(..., description="Number of scenes")
    cost_per_scene: float = Field(0.25, description="Cost per scene in USD")
    script_generation_cost: float = Field(0.01, description="Script generation cost")
    total_estimated_cost: float = Field(..., description="Total estimated cost")
    budget_limit: float = Field(..., description="Project budget limit")
    within_budget: bool = Field(..., description="Whether project is within budget")

class APIResponse(BaseModel):
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if failed")
