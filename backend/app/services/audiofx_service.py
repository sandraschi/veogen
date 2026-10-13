"""
AudioFX sound design helper.
"""

from __future__ import annotations

import base64
import logging
import uuid
from typing import Dict

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AudioFXService:
    """Thin wrapper around Google's AudioFX endpoints."""

    def __init__(self):
        self.enabled = settings.AUDIOFX_ENABLED
        self.base_url = settings.AUDIOFX_API_BASE_URL.rstrip("/")
        self.model = settings.AUDIOFX_MODEL

    async def generate_effect(
        self,
        prompt: str,
        duration_seconds: int,
        category: str,
        loop: bool,
        bpm: int,
        intensity: str,
    ) -> Dict[str, str]:
        if not self.enabled:
            raise RuntimeError("AudioFX disabled")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "durationSeconds": duration_seconds,
            "category": category,
            "loop": loop,
            "bpm": bpm,
            "intensity": intensity,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}:generate",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            audio_b64 = result.get("audio", "")
            audio_bytes = base64.b64decode(audio_b64) if audio_b64 else b""
            filename = f"audiofx_{uuid.uuid4()}.wav"
            output_path = f"{settings.OUTPUT_DIR}/{filename}"
            with open(output_path, "wb") as fp:
                fp.write(audio_bytes)
            return {
                "file": output_path,
                "audio_data": f"data:audio/wav;base64,{audio_b64}" if audio_b64 else None,
                "synthid_hash": result.get("synthId"),
                "metadata": result,
            }

    def _headers(self) -> Dict[str, str]:
        api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        if not api_key:
            raise RuntimeError("AudioFX API key missing")
        return {"Authorization": f"Bearer {api_key}"}


audiofx_service = AudioFXService()
