"""
Authentication endpoints for user management
"""

from datetime import timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
import re

from app.database import get_db, User
from app.services.auth_service import auth_service
from app.services.api_key_service import api_key_service
from app.api.deps import get_current_user, get_current_user_optional

router = APIRouter()

# Pydantic models for request/response
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: str

class UserProfile(BaseModel):
    id: str
    email: str
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    plan: str
    is_verified: bool
    created_at: Optional[str]
    last_login: Optional[str]
    settings: Dict[str, Any]

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class APIKeyCreate(BaseModel):
    service_name: str
    key_name: str
    api_key: str

class APIKeyResponse(BaseModel):
    id: int
    service_name: str
    key_name: str
    is_active: bool
    created_at: Optional[str]
    last_used: Optional[str]
    usage_count: int

class SettingUpdate(BaseModel):
    key: str
    value: Any
    value_type: str = "string"

# Authentication endpoints
@router.post("/register", response_model=Token)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
    request: Request = None,
    background_tasks: BackgroundTasks = None
):
    """Register a new user"""
    try:
        # Create user
        user = auth_service.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            username=user_data.username
        )
        # Update profile if full_name provided
        if user_data.full_name:
            auth_service.update_user_profile(db, user.id, full_name=user_data.full_name)
        # Send verification email
        if background_tasks:
            background_tasks.add_task(auth_service.send_verification_email, db, user)
        else:
            auth_service.send_verification_email(db, user)
        # Create access token
        access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
        access_token = auth_service.create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        # Create session
        ip_address = request.client.host if request else None
        user_agent = request.headers.get("user-agent") if request else None
        session_token = auth_service.create_user_session(
            db, user.id, ip_address, user_agent
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": auth_service.access_token_expire_minutes * 60,
            "user_id": user.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Login user"""
    # Authenticate user
    user = auth_service.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    # Create session
    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None
    session_token = auth_service.create_user_session(
        db, user.id, ip_address, user_agent
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": auth_service.access_token_expire_minutes * 60,
        "user_id": user.id
    }

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Logout user"""
    # Get session token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        # In a real implementation, you'd store session tokens separately
        # For now, we'll just return success
        return {"message": "Successfully logged out"}

# User profile endpoints
@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user profile"""
    profile = auth_service.get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    return profile

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    updated_user = auth_service.update_user_profile(
        db, current_user.id, **profile_data.dict(exclude_unset=True)
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    profile = auth_service.get_user_profile(db, current_user.id)
    return profile

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    success = auth_service.change_password(
        db, current_user.id, password_data.current_password, password_data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    return {"message": "Password changed successfully"}

# Settings endpoints
@router.get("/settings")
async def get_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user settings"""
    from app.database import UserSettings, get_user_setting
    
    settings = {}
    for setting in db.query(UserSettings).filter(UserSettings.user_id == current_user.id).all():
        settings[setting.setting_key] = get_user_setting(db, current_user.id, setting.setting_key)
    
    return settings

@router.put("/settings")
async def update_setting(
    setting_data: SettingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a user setting"""
    from app.database import set_user_setting
    
    set_user_setting(
        db, current_user.id, setting_data.key, setting_data.value, setting_data.value_type
    )
    return {"message": "Setting updated successfully"}

# API Key management endpoints
@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key"""
    try:
        api_key_record = api_key_service.store_api_key(
            db, current_user.id, api_key_data.service_name, 
            api_key_data.key_name, api_key_data.api_key
        )
        
        return {
            "id": api_key_record.id,
            "service_name": api_key_record.service_name,
            "key_name": api_key_record.key_name,
            "is_active": api_key_record.is_active,
            "created_at": api_key_record.created_at.isoformat() if api_key_record.created_at else None,
            "last_used": api_key_record.last_used.isoformat() if api_key_record.last_used else None,
            "usage_count": api_key_record.usage_count
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all API keys for the current user"""
    api_keys = api_key_service.list_api_keys(db, current_user.id)
    return api_keys

@router.get("/api-keys/{service_name}", response_model=List[APIKeyResponse])
async def get_service_api_keys(
    service_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get API keys for a specific service"""
    api_keys = api_key_service.get_service_keys(db, current_user.id, service_name)
    return api_keys

@router.put("/api-keys/{key_id}")
async def update_api_key(
    key_id: int,
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing API key"""
    success = api_key_service.update_api_key(
        db, current_user.id, key_id, api_key_data.api_key
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return {"message": "API key updated successfully"}

@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an API key"""
    success = api_key_service.delete_api_key(db, current_user.id, key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return {"message": "API key deleted successfully"}

@router.post("/api-keys/{key_id}/deactivate")
async def deactivate_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate an API key"""
    success = api_key_service.deactivate_api_key(db, current_user.id, key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return {"message": "API key deactivated successfully"}

@router.post("/api-keys/{key_id}/activate")
async def activate_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate an API key"""
    success = api_key_service.activate_api_key(db, current_user.id, key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return {"message": "API key activated successfully"}

# Usage statistics
@router.get("/usage-stats")
async def get_usage_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user usage statistics"""
    usage_stats = auth_service.get_user_usage_stats(db, current_user.id)
    api_key_stats = api_key_service.get_api_key_usage_stats(db, current_user.id)
    
    return {
        "generation_stats": usage_stats,
        "api_key_stats": api_key_stats
    }

@router.get("/verify-email")
async def verify_email(user: str, token: str, db: Session = Depends(get_db)):
    """Verify user email address"""
    success = auth_service.verify_email(db, user, token)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    return {"message": "Email verified successfully"}

class LostPasswordRequest(BaseModel):
    email: EmailStr

@router.post("/lost-password")
async def lost_password(
    data: LostPasswordRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Request a password reset email"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"message": "If the email exists, a reset link will be sent."}
    if background_tasks:
        background_tasks.add_task(auth_service.send_password_reset_email, db, user)
    else:
        auth_service.send_password_reset_email(db, user)
    return {"message": "If the email exists, a reset link will be sent."}

class PasswordResetRequest(BaseModel):
    user: str
    token: str
    new_password: str

@router.post("/reset-password")
async def reset_password(
    data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Reset password using token"""
    success = auth_service.reset_password(db, data.user, data.token, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    return {"message": "Password reset successfully"} 