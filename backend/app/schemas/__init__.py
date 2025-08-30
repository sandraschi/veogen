# Schemas package for VeoGen API

from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfile,
    UserLoginRequest,
    UserLoginResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserSettingsUpdate,
    UserSessionInfo,
)

from .image import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    ImageProcessingRequest,
    ImageProcessingResponse,
)

from .music import (
    MusicGenerationRequest,
    MusicGenerationResponse,
    PlaylistRequest,
    PlaylistResponse,
)

from .user_settings import (
    UserSettingsBase,
    UserSettingsCreate,
    UserSettingsUpdate as UserSettingsUpdateSchema,
    UserSettingsResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate", 
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    "UserLoginRequest",
    "UserLoginResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "UserSettingsUpdate",
    "UserSessionInfo",
    # Image schemas
    "ImageGenerationRequest",
    "ImageGenerationResponse", 
    "ImageProcessingRequest",
    "ImageProcessingResponse",
    # Music schemas
    "MusicGenerationRequest",
    "MusicGenerationResponse",
    "PlaylistRequest",
    "PlaylistResponse",
    # Settings schemas
    "UserSettingsBase",
    "UserSettingsCreate",
    "UserSettingsUpdateSchema",
    "UserSettingsResponse",
]
