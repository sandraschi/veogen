"""
Database models for Google Flow orchestration sync.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class FlowProject(Base):
    """High-level Flow workspace project metadata."""

    __tablename__ = "flow_projects"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    synopsis = Column(Text)
    status = Column(String, default="draft")
    region = Column(String, default="us")
    owner_email = Column(String, index=True)
    poster_frame_url = Column(String)
    flow_metadata = Column(JSON, default=dict)  # renamed: 'metadata' is reserved by SQLAlchemy
    last_flow_sync = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scenes = relationship(
        "FlowScene",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="FlowScene.order_index",
    )
    ingredients = relationship(
        "FlowIngredient",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class FlowScene(Base):
    """Scene/shot level information mirrored from Flow."""

    __tablename__ = "flow_scenes"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("flow_projects.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    order_index = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=10)
    status = Column(String, default="draft")
    veo_job_id = Column(String, index=True)
    prompt = Column(Text)
    camera_directions = Column(Text)
    style = Column(String, default="cinematic")
    aspect_ratio = Column(String, default="16:9")
    reference_frames = Column(JSON, default=list)
    audio_notes = Column(Text)
    checklist = Column(JSON, default=dict)
    flow_metadata = Column(JSON, default=dict)  # renamed: 'metadata' is reserved by SQLAlchemy
    poster_frame_url = Column(String)
    last_rendered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("FlowProject", back_populates="scenes")
    captions = relationship(
        "SceneCaption",
        back_populates="scene",
        cascade="all, delete-orphan",
        order_by="SceneCaption.created_at.desc()",
    )


class FlowIngredient(Base):
    """Characters, locations, props, or styles referenced by Flow."""

    __tablename__ = "flow_ingredients"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("flow_projects.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    ingredient_type = Column(String, nullable=False)  # character, location, prop, style
    description = Column(Text)
    reference_image_url = Column(String)
    flow_metadata = Column(JSON, default=dict)  # renamed: 'metadata' is reserved by SQLAlchemy
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("FlowProject", back_populates="ingredients")

    __table_args__ = (
        UniqueConstraint("project_id", "name", "ingredient_type", name="unique_flow_ingredient"),
    )


class SceneCaption(Base):
    """Scene description generated via Gemini Scene Describer."""

    __tablename__ = "scene_captions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scene_id = Column(String, ForeignKey("flow_scenes.id", ondelete="CASCADE"))
    caption = Column(Text, nullable=False)
    safety_labels = Column(JSON, default=list)
    accessibility_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, default="scene-describer")
    is_active = Column(Boolean, default=True)

    scene = relationship("FlowScene", back_populates="captions")

