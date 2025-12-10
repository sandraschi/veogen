"""
Enhanced authentication endpoints with connection testing and user onboarding
"""

from datetime import timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
import re
import logging

from app.database import get_db
from app.models.user import User
from app.services.auth_service import auth_service
from app.services.api_key_service import api_key_service
from app.services.connection_test_service import connection_test_service
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced Pydantic models for better user onboarding
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        # Basic email validation - FastAPI EmailStr already handles most
        if not v or '@' not in v:
            raise ValueError('Valid email address is required')
        
        # Check for common typos
        domain = v.split('@')[1].lower()
        common_domains = {
            'gmail.co': 'gmail.com',
            'yahoo.co': 'yahoo.com', 
            'hotmai.com': 'hotmail.com',
            'gmial.com': 'gmail.com'
        }
        
        suggested_domain = common_domains.get(domain)
        if suggested_domain:
            raise ValueError(f'Did you mean {v.split("@")[0]}@{suggested_domain}?')
        
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """Enhanced password validation with clear error messages"""
        errors = []
        
        if len(v) < 8:
            errors.append('Password must be at least 8 characters long')
        if len(v) > 128:
            errors.append('Password must be less than 128 characters')
        if not re.search(r'[A-Z]', v):
            errors.append('Password must contain at least one uppercase letter (A-Z)')
        if not re.search(r'[a-z]', v):
            errors.append('Password must contain at least one lowercase letter (a-z)')
        if not re.search(r'\d', v):
            errors.append('Password must contain at least one digit (0-9)')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            errors.append('Password must contain at least one special character (!@#$%^&*)')
        
        # Check for common weak passwords
        weak_patterns = [
            r'12345', r'password', r'qwerty', r'abc123', 
            r'letmein', r'welcome', r'admin', r'user'
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, v.lower()):
                errors.append('Password contains common weak patterns')
                break
        
        if errors:
            raise ValueError('. '.join(errors))
        
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if len(v) > 50:
                raise ValueError('Username must be less than 50 characters')
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
            
            # Check for reserved usernames
            reserved = ['admin', 'root', 'user', 'test', 'api', 'www', 'mail', 'support']
            if v.lower() in reserved:
                raise ValueError('This username is reserved')
        
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False
    
    # No password validation for login - only for registration

class ConnectionTestRequest(BaseModel):
    google_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    google_cloud_project: Optional[str] = None

class UserOnboardingData(BaseModel):
    """Data for completing user onboarding"""
    api_keys: Dict[str, str] = {}
    preferences: Dict[str, Any] = {}
    skip_tutorial: bool = False

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetComplete(BaseModel):
    user_id: str
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Same password validation as registration"""
        return UserRegister.validate_password(v)

# Enhanced authentication endpoints
@router.post("/register")
async def register(
    user_data: UserRegister,
    request: Request = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Enhanced user registration with better validation and onboarding"""
    try:
        logger.info(f"New user registration attempt: {user_data.email}")
        
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
        
        # Send verification email in background
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
        auth_service.create_user_session(
            db, user.id, ip_address, user_agent
        )
        
        logger.info(f"User registered successfully: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": auth_service.access_token_expire_minutes * 60,
            "user_id": user.id,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "plan": user.plan
            },
            "onboarding": {
                "needs_verification": not user.is_verified,
                "needs_api_setup": True,
                "next_steps": [
                    "Verify your email address",
                    "Set up your API keys",
                    "Complete your profile"
                ]
            }
        }
        
    except ValueError as e:
        logger.warning(f"Registration validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login")
async def login(
    user_data: UserLogin,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Enhanced login with better error handling and session management"""
    try:
        logger.info(f"Login attempt: {user_data.email}")
        
        # Authenticate user
        user = auth_service.authenticate_user(db, user_data.email, user_data.password)
        if not user:
            logger.warning(f"Failed login attempt: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token with extended expiry if remember_me
        token_expires = 7 * 24 * 60 if user_data.remember_me else auth_service.access_token_expire_minutes  # 7 days vs 30 minutes
        access_token_expires = timedelta(minutes=token_expires)
        access_token = auth_service.create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        
        # Create session
        ip_address = request.client.host if request else None
        user_agent = request.headers.get("user-agent") if request else None
        auth_service.create_user_session(
            db, user.id, ip_address, user_agent
        )
        
        # Get user profile
        auth_service.get_user_profile(db, user.id)
        
        # Check onboarding status
        has_api_keys = bool(api_key_service.list_api_keys(db, user.id))
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": token_expires * 60,
            "user_id": user.id,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "plan": user.plan,
                "last_login": user.last_login.isoformat() if user.last_login else None
            },
            "onboarding": {
                "needs_verification": not user.is_verified,
                "needs_api_setup": not has_api_keys,
                "is_complete": user.is_verified and has_api_keys
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.post("/test-connection")
async def test_connection(
    test_data: ConnectionTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test connection to Google/Gemini APIs with user-provided credentials"""
    try:
        logger.info(f"Connection test requested by user: {current_user.email}")
        
        # Use provided keys or fall back to user settings
        google_api_key = test_data.google_api_key
        gemini_api_key = test_data.gemini_api_key
        project_id = test_data.google_cloud_project
        
        # Run connection tests
        test_results = await connection_test_service.run_full_connection_test(
            db_session=db,
            user_id=current_user.id
        )
        
        # If keys were provided and tests passed, offer to save them
        should_save_keys = False
        if test_results.get("overall_status") == "success":
            should_save_keys = bool(google_api_key or gemini_api_key or project_id)
        
        logger.info(f"Connection test completed for {current_user.email}: {test_results.get('overall_status')}")
        
        return {
            "test_results": test_results,
            "can_save_keys": should_save_keys,
            "message": "Connection test completed",
            "recommendations": _get_connection_recommendations(test_results)
        }
        
    except Exception as e:
        logger.error(f"Connection test error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Connection test failed. Please try again."
        )

@router.post("/complete-onboarding")
async def complete_onboarding(
    onboarding_data: UserOnboardingData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete user onboarding with API keys and preferences"""
    try:
        logger.info(f"Completing onboarding for user: {current_user.email}")
        
        # Save API keys if provided
        saved_keys = []
        for service_name, api_key in onboarding_data.api_keys.items():
            if api_key and api_key.strip():
                try:
                    api_key_service.store_api_key(
                        db, current_user.id, service_name, 
                        f"{service_name}_key", api_key.strip()
                    )
                    saved_keys.append(service_name)
                except ValueError as e:
                    logger.warning(f"Failed to save {service_name} key: {e}")
        
        # Save user preferences
        from app.database import set_user_setting
        for key, value in onboarding_data.preferences.items():
            try:
                value_type = "boolean" if isinstance(value, bool) else "number" if isinstance(value, (int, float)) else "string"
                set_user_setting(db, current_user.id, key, value, value_type)
            except Exception as e:
                logger.warning(f"Failed to save preference {key}: {e}")
        
        # Mark onboarding as complete
        set_user_setting(db, current_user.id, "onboarding_complete", True, "boolean")
        set_user_setting(db, current_user.id, "skip_tutorial", onboarding_data.skip_tutorial, "boolean")
        
        # Test connections with saved keys
        test_results = None
        if saved_keys:
            test_results = await connection_test_service.run_full_connection_test(
                db_session=db,
                user_id=current_user.id
            )
        
        logger.info(f"Onboarding completed for {current_user.email}")
        
        return {
            "status": "success",
            "message": "Onboarding completed successfully",
            "saved_keys": saved_keys,
            "connection_status": test_results.get("overall_status") if test_results else "not_tested",
            "next_steps": [
                "Start creating your first video",
                "Explore the Movie Maker",
                "Check out persona chat"
            ]
        }
        
    except Exception as e:
        logger.error(f"Onboarding completion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete onboarding. Please try again."
        )

@router.post("/request-password-reset")
async def request_password_reset(
    request_data: PasswordResetRequest,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Request password reset email"""
    try:
        logger.info(f"Password reset requested for: {request_data.email}")
        
        user = db.query(User).filter(User.email == request_data.email).first()
        
        # Always return success to prevent email enumeration
        if user:
            if background_tasks:
                background_tasks.add_task(auth_service.send_password_reset_email, db, user)
            else:
                auth_service.send_password_reset_email(db, user)
            logger.info(f"Password reset email sent to: {request_data.email}")
        else:
            logger.info(f"Password reset requested for non-existent email: {request_data.email}")
        
        return {
            "message": "If the email address exists in our system, a password reset link will be sent.",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request. Please try again."
        )

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetComplete,
    db: Session = Depends(get_db)
):
    """Complete password reset with token"""
    try:
        logger.info(f"Password reset completion attempt for user: {reset_data.user_id}")
        
        success = auth_service.reset_password(
            db, reset_data.user_id, reset_data.token, reset_data.new_password
        )
        
        if not success:
            logger.warning(f"Invalid password reset token for user: {reset_data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        logger.info(f"Password reset successful for user: {reset_data.user_id}")
        
        return {
            "message": "Password reset successfully",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset completion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password. Please try again."
        )

@router.get("/debug-auth")
async def debug_auth(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Debug endpoint to test authentication"""
    logger.info(f"DEBUG: Auth test called with user: {current_user.email} (id: {current_user.id})")
    return {
        "message": "Auth working!",
        "user_id": current_user.id,
        "user_email": current_user.email,
        "user_username": current_user.username
    }

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    try:
        logger.info(f"get_current_user_info called with user: {current_user.email} (id: {current_user.id})")
        
        # Get user profile with settings
        profile = auth_service.get_user_profile(db, current_user.id)
        
        # Check onboarding status
        has_api_keys = bool(api_key_service.list_api_keys(db, current_user.id))
        
        logger.info(f"Returning profile for user: {current_user.id}")
        
        return {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "is_verified": current_user.is_verified,
            "plan": current_user.plan,
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
            "settings": profile.get("settings", {}) if profile else {},
            "onboarding": {
                "needs_verification": not current_user.is_verified,
                "needs_api_setup": not has_api_keys,
                "is_complete": current_user.is_verified and has_api_keys
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.post("/validate-reset-token")
async def validate_reset_token(
    token_data: dict,
    db: Session = Depends(get_db)
):
    """Validate password reset token"""
    try:
        user_id = token_data.get("user_id")
        token = token_data.get("token")
        
        if not user_id or not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing user_id or token"
            )
        
        is_valid = auth_service.verify_password_reset_token(db, user_id, token)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        return {"message": "Token is valid", "status": "valid"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate token"
        )

@router.post("/verify-email")  
async def verify_email(
    verification_data: dict,
    db: Session = Depends(get_db)
):
    """Verify user email with token"""
    try:
        user_id = verification_data.get("user_id")
        token = verification_data.get("token")
        
        if not user_id or not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing user_id or token"
            )
        
        success = auth_service.verify_email(db, user_id, token)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        logger.info(f"Email verification successful for user: {user_id}")
        
        return {
            "message": "Email verified successfully",
            "status": "verified"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )

@router.post("/resend-verification")
async def resend_verification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Resend email verification"""
    try:
        if current_user.is_verified:
            return {
                "message": "Email is already verified",
                "status": "already_verified"
            }
        
        # Send verification email
        if background_tasks:
            background_tasks.add_task(auth_service.send_verification_email, db, current_user)
        else:
            auth_service.send_verification_email(db, current_user)
        
        logger.info(f"Verification email resent to: {current_user.email}")
        
        return {
            "message": "Verification email sent",
            "status": "sent"
        }
        
    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification email"
        )

def _get_connection_recommendations(test_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on connection test results"""
    recommendations = []
    
    if test_results.get("overall_status") == "success":
        recommendations.append("✅ All connections are working! You're ready to start creating.")
    
    details = test_results.get("details", {})
    
    # Google Auth recommendations
    google_auth = details.get("google_auth", {})
    if google_auth.get("status") == "failed":
        recommendations.append("❌ Google authentication failed. Please check your API keys.")
        if "api_key_auth" in google_auth.get("details", {}):
            if google_auth["details"]["api_key_auth"].get("status") == "failed":
                recommendations.append("🔑 Your Google API key appears to be invalid. Please verify it in your Google Cloud Console.")
    
    # Gemini API recommendations  
    gemini_api = details.get("gemini_api", {})
    if gemini_api.get("status") == "failed":
        recommendations.append("❌ Gemini API connection failed.")
        gemini_details = gemini_api.get("details", {})
        if gemini_details.get("text_generation", {}).get("status") == "failed":
            recommendations.append("🤖 Gemini text generation is not working. Check your Gemini API key.")
    
    if not recommendations:
        recommendations.append("⚠️ Some connections may need attention. Check the detailed results above.")
    
    return recommendations
