# Schemas package for VeoGen API

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
from .user import (
    PasswordResetConfirm,
    PasswordResetRequest,
    UserBase,
    UserCreate,
    UserLoginRequest,
    UserLoginResponse,
    UserProfile,
    UserResponse,
    UserSessionInfo,
    UserSettingsUpdate,
    UserUpdate,
)
from .user_settings import (
    UserSettingsBase,
    UserSettingsCreate,
    UserSettingsResponse,
)
from .user_settings import (
    UserSettingsUpdate as UserSettingsUpdateSchema,
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
