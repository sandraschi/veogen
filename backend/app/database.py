"""
Database configuration and session management for VeoGen
"""

import os
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from datetime import datetime
import json

# Database URL from config
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./veogen.db")

# Create async engine for SQLAlchemy 2.0 style
if DATABASE_URL.startswith("sqlite"):
    # Convert to async SQLite URL
    async_database_url = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    # For PostgreSQL, MySQL, etc.
    async_database_url = DATABASE_URL.replace("://", "+asyncpg://")

# Create engines
engine = create_engine(DATABASE_URL, echo=False)
async_engine = create_async_engine(async_database_url, echo=False)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Create base class for models
Base = declarative_base()

# Database Models
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

class APIKey(Base):
    """API keys and credentials storage"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    service_name = Column(String, nullable=False)  # gemini, openai, etc.
    key_name = Column(String, nullable=False)  # display name for the key
    encrypted_key = Column(Text, nullable=False)  # encrypted API key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)

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

class GenerationHistory(Base):
    """History of AI generations"""
    __tablename__ = "generation_history"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    project_id = Column(String, index=True)
    generation_type = Column(String, nullable=False)  # video, image, music, text
    prompt = Column(Text, nullable=False)
    result_url = Column(String)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    generation_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
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

# Database session management
def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Database initialization
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    # Create default admin user if not exists
    db = SessionLocal()
    from app.services.auth_service import AuthService
    auth = AuthService()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            id="admin",
            email="admin@localhost",
            username="admin",
            hashed_password=auth.hash_password("admin"),
            is_active=True,
            is_verified=True,
            plan="admin",
            created_at=datetime.utcnow(),
            full_name="Administrator"
        )
        db.add(admin)
        db.commit()
    db.close()

async def init_async_db():
    """Initialize database tables asynchronously"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Utility functions for settings management
def get_user_setting(db: Session, user_id: str, key: str, default=None):
    """Get a user setting"""
    setting = db.query(UserSettings).filter(
        UserSettings.user_id == user_id,
        UserSettings.setting_key == key
    ).first()
    
    if not setting:
        return default
    
    # Convert based on type
    if setting.setting_type == "json":
        return json.loads(setting.setting_value) if setting.setting_value else default
    elif setting.setting_type == "boolean":
        return setting.setting_value.lower() == "true" if setting.setting_value else default
    elif setting.setting_type == "number":
        return float(setting.setting_value) if setting.setting_value else default
    else:
        return setting.setting_value or default

def set_user_setting(db: Session, user_id: str, key: str, value, value_type="string"):
    """Set a user setting"""
    # Convert value to string for storage
    if value_type == "json":
        value_str = json.dumps(value) if value else None
    elif value_type == "boolean":
        value_str = str(value).lower() if value is not None else None
    elif value_type == "number":
        value_str = str(value) if value is not None else None
    else:
        value_str = str(value) if value is not None else None
    
    # Check if setting exists
    setting = db.query(UserSettings).filter(
        UserSettings.user_id == user_id,
        UserSettings.setting_key == key
    ).first()
    
    if setting:
        setting.setting_value = value_str
        setting.setting_type = value_type
        setting.updated_at = datetime.utcnow()
    else:
        setting = UserSettings(
            user_id=user_id,
            setting_key=key,
            setting_value=value_str,
            setting_type=value_type
        )
        db.add(setting)
    
    db.commit()
    return setting

# Initialize database on import
init_db() 