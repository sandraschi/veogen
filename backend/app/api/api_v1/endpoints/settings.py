from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.api.deps import get_current_user, get_current_user_optional
from app.schemas.user_settings import UserSettingsRequest, UserSettingsResponse
from app.services.user_settings_service import UserSettingsService

router = APIRouter()

@router.get("/", response_model=UserSettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get current user's settings"""
    if not current_user:
        # Return default settings for anonymous users
        return UserSettingsResponse()
    
    try:
        settings = UserSettingsService.get_user_settings(db, current_user.id)
        return settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve settings"
        )

@router.post("/", response_model=UserSettingsResponse)
async def update_settings(
    settings_data: UserSettingsRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Update current user's settings"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to save settings"
        )
    
    try:
        updated_settings = UserSettingsService.update_user_settings(
            db, current_user.id, settings_data
        )
        return updated_settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings"
        )

@router.get("/{setting_key}")
async def get_setting(
    setting_key: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get a specific setting"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        value = UserSettingsService.get_setting(db, current_user.id, setting_key)
        return {"key": setting_key, "value": value}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve setting"
        )

@router.post("/{setting_key}")
async def set_setting(
    setting_key: str,
    value: dict,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Set a specific setting"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        setting_value = value.get("value")
        setting_type = value.get("type", "string")
        
        UserSettingsService.set_setting(
            db, current_user.id, setting_key, setting_value, setting_type
        )
        
        return {"key": setting_key, "value": setting_value, "type": setting_type}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update setting"
        ) 