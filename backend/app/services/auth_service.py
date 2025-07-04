"""
Authentication and user management service
"""

import os
import uuid
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database import User, UserSession, get_user_setting, set_user_setting, PasswordResetToken, UserSettings
from app.config import settings
import secrets
from app.services.email_service import send_email

class AuthService:
    """Authentication service for user management"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None
    
    def create_user(self, db: Session, email: str, password: str, username: Optional[str] = None) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        
        if username:
            existing_username = db.query(User).filter(User.username == username).first()
            if existing_username:
                raise ValueError("Username already taken")
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = self.hash_password(password)
        
        user = User(
            id=user_id,
            email=email,
            username=username,
            hashed_password=hashed_password,
            created_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Set default user settings
        self.set_default_user_settings(db, user_id)
        
        return user
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    def create_user_session(self, db: Session, user_id: str, ip_address: Optional[str] = None, 
                           user_agent: Optional[str] = None) -> str:
        """Create a new user session"""
        session_id = str(uuid.uuid4())
        session_token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=30)  # 30 day session
        
        session = UserSession(
            id=session_id,
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(session)
        db.commit()
        
        return session_token
    
    def validate_session(self, db: Session, session_token: str) -> Optional[User]:
        """Validate a session token and return the user"""
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        # Update last activity
        session.last_activity = datetime.utcnow()
        db.commit()
        
        # Get user
        user = db.query(User).filter(User.id == session.user_id).first()
        return user if user and user.is_active else None
    
    def logout_user(self, db: Session, session_token: str) -> bool:
        """Logout a user by invalidating their session"""
        session = db.query(UserSession).filter(UserSession.session_token == session_token).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    
    def set_default_user_settings(self, db: Session, user_id: str):
        """Set default settings for a new user"""
        default_settings = {
            "theme": "light",
            "language": "en",
            "notifications_enabled": True,
            "auto_save": True,
            "default_video_duration": 5,
            "default_video_style": "cinematic",
            "quality_preference": "high",
            "storage_quota": 1024,  # MB
            "api_usage_limit": 100  # requests per day
        }
        
        for key, value in default_settings.items():
            value_type = "boolean" if isinstance(value, bool) else "number" if isinstance(value, (int, float)) else "string"
            set_user_setting(db, user_id, key, value, value_type)
    
    def get_user_profile(self, db: Session, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile with settings"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Get user settings
        settings = {}
        for setting in db.query(UserSettings).filter(UserSettings.user_id == user_id).all():
            settings[setting.setting_key] = get_user_setting(db, user_id, setting.setting_key)
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "plan": user.plan,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "settings": settings
        }
    
    def update_user_profile(self, db: Session, user_id: str, **kwargs) -> Optional[User]:
        """Update user profile information"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Update allowed fields
        allowed_fields = ["username", "full_name", "avatar_url"]
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        return user
    
    def change_password(self, db: Session, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Verify current password
        if not self.verify_password(current_password, user.hashed_password):
            return False
        
        # Hash and set new password
        user.hashed_password = self.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return True
    
    def get_user_usage_stats(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get user usage statistics"""
        from app.database import GenerationHistory
        
        # Get generation history
        generations = db.query(GenerationHistory).filter(
            GenerationHistory.user_id == user_id
        ).all()
        
        # Calculate stats
        total_generations = len(generations)
        successful_generations = len([g for g in generations if g.status == "completed"])
        failed_generations = len([g for g in generations if g.status == "failed"])
        
        # Get recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_generations = [g for g in generations if g.created_at >= thirty_days_ago]
        
        return {
            "total_generations": total_generations,
            "successful_generations": successful_generations,
            "failed_generations": failed_generations,
            "success_rate": (successful_generations / total_generations * 100) if total_generations > 0 else 0,
            "recent_activity": len(recent_generations),
            "last_generation": max([g.created_at for g in generations]) if generations else None
        }

    def generate_token(self, length=32) -> str:
        return secrets.token_urlsafe(length)

    def send_verification_email(self, db: Session, user: User):
        token = self.generate_token(24)
        user.email_verification_token = token
        user.email_verification_sent_at = datetime.utcnow()
        db.commit()
        verify_url = f"https://yourdomain.com/verify-email?token={token}&user={user.id}"
        subject = "Verify your VeoGen account"
        body = f"Hello {user.username or user.email},\n\nPlease verify your email by clicking the link below:\n{verify_url}\n\nIf you did not register, ignore this email."
        send_email(user.email, subject, body)

    def verify_email(self, db: Session, user_id: str, token: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.email_verification_token != token:
            return False
        user.is_verified = True
        user.email_verification_token = None
        db.commit()
        return True

    def send_password_reset_email(self, db: Session, user: User):
        token = self.generate_token(24)
        expires_at = datetime.utcnow() + timedelta(hours=2)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            used=False
        )
        db.add(reset_token)
        db.commit()
        reset_url = f"https://yourdomain.com/reset-password?token={token}&user={user.id}"
        subject = "VeoGen Password Reset"
        body = f"Hello {user.username or user.email},\n\nTo reset your password, click the link below:\n{reset_url}\n\nIf you did not request a password reset, ignore this email."
        send_email(user.email, subject, body)

    def verify_password_reset_token(self, db: Session, user_id: str, token: str) -> bool:
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        return bool(reset_token)

    def reset_password(self, db: Session, user_id: str, token: str, new_password: str) -> bool:
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        if not reset_token:
            return False
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        user.hashed_password = self.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        reset_token.used = True
        db.commit()
        return True

# Global auth service instance
auth_service = AuthService() 