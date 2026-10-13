from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional
from app.database import get_db
from app.models.user import User
from app.schemas.user_settings import UserSettingsRequest, UserSettingsResponse
from app.services.user_settings_service import UserSettingsService

router = APIRouter()


class SettingUpdate(BaseModel):
    key: str
    value: Any
    value_type: Optional[str] = "string"


@router.get("/", response_model=UserSettingsResponse)
async def get_settings(current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    """Get current user's settings"""
    if not current_user:
        # Return default settings for anonymous users
        return UserSettingsResponse()

    try:
        settings = UserSettingsService.get_user_settings(db, current_user.id)
        return settings
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve settings")


@router.post("/", response_model=UserSettingsResponse)
async def update_settings_post(
    settings_data: UserSettingsRequest,
    current_user: User = Depends(get_current_user),  # Required authentication
    db: Session = Depends(get_db),
):
    """Update current user's settings via POST - requires authentication"""
    try:
        updated_settings = UserSettingsService.update_user_settings(db, current_user.id, settings_data)
        return updated_settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update settings: {str(e)}"
        )


@router.put("/", response_model=UserSettingsResponse)
async def update_settings_put(
    settings_data: SettingUpdate,
    current_user: User = Depends(get_current_user),  # Required authentication
    db: Session = Depends(get_db),
):
    """Update a single user setting via PUT - requires authentication"""
    try:
        # Convert single setting to the format expected by the service
        UserSettingsService.set_setting(
            db, current_user.id, settings_data.key, settings_data.value, settings_data.value_type
        )

        # Return updated settings
        updated_settings = UserSettingsService.get_user_settings(db, current_user.id)
        return updated_settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update setting: {str(e)}"
        )


@router.get("/{setting_key}")
async def get_setting(
    setting_key: str,
    current_user: User = Depends(get_current_user),  # Required authentication
    db: Session = Depends(get_db),
):
    """Get a specific setting - requires authentication"""
    try:
        value = UserSettingsService.get_setting(db, current_user.id, setting_key)
        return {"key": setting_key, "value": value}
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve setting")


@router.post("/{setting_key}")
async def set_setting(
    setting_key: str,
    value: dict,
    current_user: User = Depends(get_current_user),  # Required authentication
    db: Session = Depends(get_db),
):
    """Set a specific setting - requires authentication"""
    try:
        setting_value = value.get("value")
        setting_type = value.get("type", "string")

        UserSettingsService.set_setting(db, current_user.id, setting_key, setting_value, setting_type)

        return {"key": setting_key, "value": setting_value, "type": setting_type}
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update setting")
