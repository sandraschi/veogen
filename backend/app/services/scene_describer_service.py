"""
Gemini-based Scene Describer helper.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from sqlalchemy.orm import Session

from app.config import settings
from app.models.flow import FlowScene, SceneCaption

logger = logging.getLogger(__name__)


class SceneDescriberService:
    """Generate accessibility captions and safety tags for Flow scenes."""

    def __init__(self):
        self.enabled = settings.SCENE_DESCRIBER_ENABLED and bool(settings.GEMINI_API_KEY)
        self.model = None
        if self.enabled:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(settings.SCENE_DESCRIBER_MODEL)
                logger.info("Scene Describer model %s ready", settings.SCENE_DESCRIBER_MODEL)
            except Exception as exc:
                logger.error("Failed to initialize Scene Describer: %s", exc)
                self.enabled = False

    async def describe_scene(
        self,
        db: Session,
        scene: FlowScene,
        reference_url: Optional[str] = None,
    ) -> SceneCaption:
        """Run Gemini vision model on poster frame or provided ref."""
        if not self.enabled or not self.model:
            raise RuntimeError("Scene Describer disabled or misconfigured")

        image_url = reference_url or scene.poster_frame_url
        if not image_url:
            raise ValueError("Scene missing poster frame")

        prompt = (
            "You are a film accessibility expert. Describe the scene in <=120 words, "
            "include emotional tone, key objects, and movement. Provide JSON with "
            "`caption` and `safetyLabels` (array)."
        )

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                [
                    {"text": prompt},
                    {"image_url": image_url},
                ],
                generation_config={
                    "response_mime_type": "application/json",
                },
            )
        except google_exceptions.GoogleAPIError as exc:
            logger.error("Gemini Scene Describer call failed: %s", exc)
            raise

        data = self._parse_response(response)
        caption_model = SceneCaption(
            scene_id=scene.id,
            caption=data.get("caption", "No caption provided"),
            safety_labels=data.get("safetyLabels", []),
            accessibility_notes=data.get("accessibilityNotes"),
        )
        db.add(caption_model)
        db.commit()
        db.refresh(caption_model)
        return caption_model

    def _parse_response(self, response) -> Dict:
        """Extract JSON body."""
        try:
            text = response.text or "{}"
            return genai.types.content_types.from_json(text)
        except Exception:
            logger.warning("Scene Describer returned non-JSON payload")
            return {"caption": response.text}


scene_describer_service = SceneDescriberService()
