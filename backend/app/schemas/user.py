# User Pydantic Schemas for VeoGen API

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    email_verification_token: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for user updates"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema for user responses"""
    id: str
    is_verified: bool = False
    plan: str = "free"
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Extended user profile schema"""
    id: str
    email: EmailStr
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    plan: str
    created_at: datetime
    last_login: Optional[datetime]
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)


class UserSettingsUpdate(BaseModel):
    """Schema for user settings updates"""
    setting_key: str
    setting_value: Any
    setting_type: str = "string"


class UserSessionInfo(BaseModel):
    """Schema for user session information"""
    id: str
    user_id: str
    expires_at: datetime
    created_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True
