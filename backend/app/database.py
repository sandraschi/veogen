"""
Database configuration and session management for VeoGen.

Phase 2 salvage: replaced the Postgres-only setup with a local SQLite
database (sync engine). The endpoint layer uses sync SQLAlchemy sessions
(db.query), so SQLite is a drop-in and removes the Postgres/Redis/Celery
infrastructure claims that were never wired up.
"""

import json
import os
from datetime import datetime
from typing import Generator

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

# SQLite works for the single-user fleet deployment; set DATABASE_URL to a
# Postgres URL to scale up later without touching the code.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import models to ensure they are registered with SQLAlchemy
from .models import flow  # noqa: F401  (ensures Flow tables are registered)
from .models.user import User, UserSettings  # noqa: E402


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


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and the default admin user."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            import bcrypt

            hashed_password = bcrypt.hashpw("admin".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            admin = User(
                id="admin",
                email="admin@localhost",
                username="admin",
                hashed_password=hashed_password,
                is_active=True,
                is_verified=True,
                plan="admin",
                created_at=datetime.utcnow(),
                full_name="Administrator",
            )
            db.add(admin)
            db.commit()
            print("Created default admin user")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def get_user_setting(db: Session, user_id: str, key: str, default=None):
    """Get a user setting"""
    setting = db.query(UserSettings).filter(UserSettings.user_id == user_id, UserSettings.setting_key == key).first()

    if not setting:
        return default

    if setting.setting_type == "json":
        return json.loads(setting.setting_value) if setting.setting_value else default
    elif setting.setting_type == "boolean":
        return setting.setting_value.lower() == "true" if setting.setting_value else default
    elif setting.setting_type == "number":
        return float(setting.setting_value) if setting.setting_value else default
    else:
        return setting.setting_value or default


def set_user_setting(db: Session, user_id: str, key: str, value, value_type: str = "string"):
    """Set or update a user setting"""
    if value_type == "json":
        value_str = json.dumps(value) if value is not None else None
    elif value_type == "boolean":
        value_str = str(value).lower() if value is not None else None
    else:
        value_str = str(value) if value is not None else None

    setting = db.query(UserSettings).filter(UserSettings.user_id == user_id, UserSettings.setting_key == key).first()

    if setting:
        setting.setting_value = value_str
        setting.setting_type = value_type
        setting.updated_at = datetime.utcnow()
    else:
        setting = UserSettings(
            user_id=user_id,
            setting_key=key,
            setting_value=value_str,
            setting_type=value_type,
        )
        db.add(setting)

    db.commit()
    return setting
