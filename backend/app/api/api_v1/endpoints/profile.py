from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.user import UserUpdate, UserResponse
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: str
    settings: Optional[dict] = None

    class Config:
        from_attributes = True

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    try:
        # Get user settings as well
        from app.services.user_settings_service import UserSettingsService
        settings = UserSettingsService.get_user_settings(db, current_user.id)
        
        profile_data = {
            "id": str(current_user.id),
            "email": current_user.email,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "avatar_url": current_user.avatar_url,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat(),
            "settings": settings.dict() if settings else None
        }
        
        return ProfileResponse(**profile_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve profile: {str(e)}"
        )

@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    try:
        # Update user fields
        if profile_data.username is not None:
            # Check if username is already taken by another user
            existing_user = db.query(User).filter(
                User.username == profile_data.username,
                User.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            current_user.username = profile_data.username
            
        if profile_data.full_name is not None:
            current_user.full_name = profile_data.full_name
            
        if profile_data.avatar_url is not None:
            current_user.avatar_url = profile_data.avatar_url
        
        # Save changes
        db.commit()
        db.refresh(current_user)
        
        # Get updated settings
        from app.services.user_settings_service import UserSettingsService
        settings = UserSettingsService.get_user_settings(db, current_user.id)
        
        profile_data = {
            "id": str(current_user.id),
            "email": current_user.email,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "avatar_url": current_user.avatar_url,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat(),
            "settings": settings.dict() if settings else None
        }
        
        return ProfileResponse(**profile_data)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
