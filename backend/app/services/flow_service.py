"""
Integration helper for Google Flow workspace sync.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.flow import FlowIngredient, FlowProject, FlowScene
from app.services.video_service import video_service

logger = logging.getLogger(__name__)


class FlowService:
    """Persist Flow webhook payloads locally and sync with Flow APIs when available."""

    def __init__(self):
        self.enabled = settings.FLOW_ENABLED
        self.base_url = settings.FLOW_API_BASE_URL.rstrip("/")
        self.default_region = settings.FLOW_DEFAULT_REGION

    # ------------------------------------------------------------------ #
    # Webhook signature helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def verify_signature(payload: bytes, signature_header: Optional[str]) -> bool:
        """Validate Flow webhook signature when secret available."""
        secret = settings.FLOW_WEBHOOK_SECRET
        if not secret:
            return True
        if not signature_header:
            return False
        digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, signature_header)

    # ------------------------------------------------------------------ #
    # Upsert helpers
    # ------------------------------------------------------------------ #
    def _upsert_project(self, db: Session, project_payload: Dict) -> FlowProject:
        project_id = project_payload.get("id") or project_payload.get("projectId")
        if not project_id:
            raise ValueError("Flow project payload missing id")

        project = db.query(FlowProject).filter(FlowProject.id == project_id).first()
        if not project:
            project = FlowProject(id=project_id)
            db.add(project)

        project.title = project_payload.get("title") or project.title or "Untitled"
        project.synopsis = project_payload.get("synopsis") or project.synopsis
        project.status = project_payload.get("status") or project.status or "draft"
        project.region = project_payload.get("region") or project.region or self.default_region
        project.owner_email = project_payload.get("ownerEmail") or project.owner_email
        project.poster_frame_url = project_payload.get("posterFrameUrl") or project.poster_frame_url
        project.flow_metadata = project_payload
        project.last_flow_sync = datetime.utcnow()
        project.updated_at = datetime.utcnow()

        return project

    def _upsert_scene(self, db: Session, project_id: str, scene_payload: Dict) -> FlowScene:
        scene_id = scene_payload.get("id") or scene_payload.get("sceneId")
        if not scene_id:
            raise ValueError("Flow scene payload missing id")

        scene = db.query(FlowScene).filter(FlowScene.id == scene_id).first()
        if not scene:
            scene = FlowScene(id=scene_id, project_id=project_id)
            db.add(scene)

        scene.title = scene_payload.get("title") or scene.title or "Untitled Scene"
        scene.order_index = scene_payload.get("orderIndex") or scene.order_index or 0
        scene.duration_seconds = scene_payload.get("durationSeconds") or scene.duration_seconds or 10
        scene.status = scene_payload.get("status") or scene.status or "draft"
        scene.veo_job_id = scene_payload.get("veoJobId") or scene.veo_job_id
        scene.prompt = scene_payload.get("prompt") or scene.prompt
        scene.camera_directions = scene_payload.get("cameraDirections") or scene.camera_directions
        scene.style = scene_payload.get("style") or scene.style or "cinematic"
        scene.aspect_ratio = scene_payload.get("aspectRatio") or scene.aspect_ratio or "16:9"
        scene.reference_frames = scene_payload.get("referenceFrames") or scene.reference_frames or []
        scene.audio_notes = scene_payload.get("audioNotes") or scene.audio_notes
        scene.checklist = scene_payload.get("checklist") or scene.checklist or {}
        scene.flow_metadata = scene_payload
        scene.poster_frame_url = scene_payload.get("posterFrameUrl") or scene.poster_frame_url
        scene.updated_at = datetime.utcnow()

        return scene

    def _sync_ingredients(self, db: Session, project_id: str, ingredients_payload: List[Dict]) -> None:
        if not ingredients_payload:
            return

        existing = db.query(FlowIngredient).filter(FlowIngredient.project_id == project_id).all()
        existing_key = {(i.name, i.ingredient_type): i for i in existing}

        for item in ingredients_payload:
            name = item.get("name")
            ingredient_type = item.get("type") or "unknown"
            if not name:
                continue
            key = (name, ingredient_type)
            ingredient = existing_key.get(key)
            if not ingredient:
                ingredient = FlowIngredient(
                    id=item.get("id") or f"{project_id}:{name}:{ingredient_type}",
                    project_id=project_id,
                    name=name,
                    ingredient_type=ingredient_type,
                )
                db.add(ingredient)
                existing_key[key] = ingredient

            ingredient.description = item.get("description") or ingredient.description
            ingredient.reference_image_url = item.get("referenceImageUrl") or ingredient.reference_image_url
            ingredient.flow_metadata = item
            ingredient.updated_at = datetime.utcnow()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def process_webhook(self, raw_body: bytes, signature: Optional[str]) -> Dict[str, str]:
        """Persist Flow payload received via webhook."""
        if not self.verify_signature(raw_body, signature):
            raise ValueError("Invalid Flow signature")

        payload = json.loads(raw_body.decode("utf-8"))
        project_payload = payload.get("project") or {}
        scenes_payload = payload.get("scenes") or []
        ingredients_payload = payload.get("ingredients") or []

        db = SessionLocal()
        try:
            project = self._upsert_project(db, project_payload)
            for scene_payload in scenes_payload:
                self._upsert_scene(db, project.id, scene_payload)
            self._sync_ingredients(db, project.id, ingredients_payload)
            db.commit()

            return {"project_id": project.id, "status": "ingested"}
        except Exception:
            db.rollback()
            logger.exception("Failed to process Flow webhook")
            raise
        finally:
            db.close()

    def list_projects(self, db: Session) -> List[FlowProject]:
        """Return stored Flow projects."""
        return db.query(FlowProject).order_by(FlowProject.updated_at.desc()).all()

    def get_project(self, db: Session, project_id: str) -> Optional[FlowProject]:
        return db.query(FlowProject).filter(FlowProject.id == project_id).first()

    async def trigger_scene_render(self, db: Session, scene: FlowScene, user_id: str) -> Dict[str, str]:
        """Kick off Veo render for a scene using stored metadata."""
        prompt = scene.prompt or scene.flow_metadata.get("prompt") if scene.flow_metadata else None
        if not prompt:
            raise ValueError("Scene missing prompt")

        result = await video_service.generate_video(
            prompt=prompt,
            duration=scene.duration_seconds or 10,
            aspect_ratio=scene.aspect_ratio or "16:9",
            style=scene.style or "cinematic",
            user_id=user_id,
        )
        if result.get("status") != "success":
            raise RuntimeError(result.get("error", "Video generation failed"))

        scene.veo_job_id = result.get("job_id")
        scene.last_rendered_at = datetime.utcnow()
        scene.status = "rendering"
        db.commit()

        return {"job_id": scene.veo_job_id, "status": "rendering"}

    # ------------------------------------------------------------------ #
    # Flow API sync (optional – requires access)
    # ------------------------------------------------------------------ #
    async def sync_project_with_flow(self, project_id: str) -> Dict[str, str]:
        """Optional proactive sync from Flow API."""
        if not self.enabled:
            raise RuntimeError("Flow integration disabled")
        endpoint = f"{self.base_url}/projects/{project_id}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(endpoint, headers=self._auth_header())
            response.raise_for_status()
            payload = response.json()
            self.process_webhook(
                json.dumps(payload).encode("utf-8"),
                signature=None,
            )
            return {"project_id": project_id, "status": "synced"}

    def _auth_header(self) -> Dict[str, str]:
        api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        if api_key:
            return {"Authorization": f"Bearer {api_key}"}
        raise RuntimeError("Flow API key not configured")


flow_service = FlowService()
