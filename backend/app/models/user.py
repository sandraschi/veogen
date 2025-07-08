# User Database Models

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer, Text
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    """User model for authentication and profile management"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_sent_at = Column(DateTime, nullable=True)
    plan = Column(String, default="free")  # free, pro, studio
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Profile information
    full_name = Column(String)
    avatar_url = Column(String)
    preferences = Column(JSON, default=dict)

    # Relationships - using string references to avoid circular imports
    music_generations = relationship(
        "MusicGenerationDB",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    image_generations = relationship(
        "ImageGeneration",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class UserSettings(Base):
    """User settings and preferences"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    setting_key = Column(String, nullable=False)
    setting_value = Column(Text)
    setting_type = Column(String, default="string")  # string, json, boolean, number
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSession(Base):
    """User session management"""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    session_token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    user_agent = Column(String)

class Project(Base):
    """User projects (videos, books, etc.)"""
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    project_type = Column(String, nullable=False)  # video, book, movie, etc.
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="draft")  # draft, processing, completed, failed
    project_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

class PasswordResetToken(Base):
    """Password reset tokens for lost password flow"""
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False) 