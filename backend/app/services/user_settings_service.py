from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from app.database import get_user_setting, set_user_setting
from app.schemas.user_settings import UserSettingsRequest, UserSettingsResponse

class UserSettingsService:
    """Service for managing user settings"""
    
    @staticmethod
    def get_user_settings(db: Session, user_id: str) -> UserSettingsResponse:
        """Get all settings for a user"""
        settings = UserSettingsResponse()
        
        # Get all settings from database
        settings.google_api_key = get_user_setting(db, user_id, "google_api_key")
        settings.google_cloud_project = get_user_setting(db, user_id, "google_cloud_project")
        settings.gemini_api_key = get_user_setting(db, user_id, "gemini_api_key")
        settings.default_style = get_user_setting(db, user_id, "default_style", "cinematic")
        settings.default_duration = get_user_setting(db, user_id, "default_duration", 5)
        settings.default_aspect_ratio = get_user_setting(db, user_id, "default_aspect_ratio", "16:9")
        settings.auto_save = get_user_setting(db, user_id, "auto_save", True)
        settings.notifications = get_user_setting(db, user_id, "notifications", True)
        settings.theme = get_user_setting(db, user_id, "theme", "dark")
        
        # Get the latest updated_at timestamp
        latest_updated = get_user_setting(db, user_id, "settings_updated_at")
        if latest_updated:
            settings.updated_at = datetime.fromisoformat(latest_updated)
        
        return settings
    
    @staticmethod
    def update_user_settings(db: Session, user_id: str, settings_data: UserSettingsRequest) -> UserSettingsResponse:
        """Update user settings"""
        # Update each setting
        if settings_data.google_api_key is not None:
            set_user_setting(db, user_id, "google_api_key", settings_data.google_api_key, "string")
        
        if settings_data.google_cloud_project is not None:
            set_user_setting(db, user_id, "google_cloud_project", settings_data.google_cloud_project, "string")
        
        if settings_data.gemini_api_key is not None:
            set_user_setting(db, user_id, "gemini_api_key", settings_data.gemini_api_key, "string")
        
        if settings_data.default_style is not None:
            set_user_setting(db, user_id, "default_style", settings_data.default_style, "string")
        
        if settings_data.default_duration is not None:
            set_user_setting(db, user_id, "default_duration", settings_data.default_duration, "number")
        
        if settings_data.default_aspect_ratio is not None:
            set_user_setting(db, user_id, "default_aspect_ratio", settings_data.default_aspect_ratio, "string")
        
        if settings_data.auto_save is not None:
            set_user_setting(db, user_id, "auto_save", settings_data.auto_save, "boolean")
        
        if settings_data.notifications is not None:
            set_user_setting(db, user_id, "notifications", settings_data.notifications, "boolean")
        
        if settings_data.theme is not None:
            set_user_setting(db, user_id, "theme", settings_data.theme, "string")
        
        # Update the settings_updated_at timestamp
        now = datetime.utcnow()
        set_user_setting(db, user_id, "settings_updated_at", now.isoformat(), "string")
        
        # Return the updated settings
        return UserSettingsService.get_user_settings(db, user_id)
    
    @staticmethod
    def get_setting(db: Session, user_id: str, key: str, default=None):
        """Get a specific setting"""
        return get_user_setting(db, user_id, key, default)
    
    @staticmethod
    def set_setting(db: Session, user_id: str, key: str, value, value_type="string"):
        """Set a specific setting"""
        return set_user_setting(db, user_id, key, value, value_type) 