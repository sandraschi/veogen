from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserSettingsRequest(BaseModel):
    google_api_key: Optional[str] = None
    google_cloud_project: Optional[str] = None
    gemini_api_key: Optional[str] = None
    default_style: Optional[str] = "cinematic"
    default_duration: Optional[int] = 5
    default_aspect_ratio: Optional[str] = "16:9"
    auto_save: Optional[bool] = True
    notifications: Optional[bool] = True
    theme: Optional[str] = "dark"

class UserSettingsResponse(BaseModel):
    google_api_key: Optional[str] = None
    google_cloud_project: Optional[str] = None
    gemini_api_key: Optional[str] = None
    default_style: str = "cinematic"
    default_duration: int = 5
    default_aspect_ratio: str = "16:9"
    auto_save: bool = True
    notifications: bool = True
    theme: str = "dark"
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 