import asyncio
import base64
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from google import genai

from app.config import settings

logger = logging.getLogger(__name__)


class LyriaProvider:
    """
    Lyria music generation via the Gemini Interactions API.

    settings.LYRIA_MODEL (lyria-3.5) makes full-length songs; settings.LYRIA_CLIP_MODEL
    (lyria-3-clip-preview) always makes 30 s clips. Output is MP3, 44.1 kHz stereo.
    See https://ai.google.dev/gemini-api/docs/music-generation
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY (or GEMINI_API_KEY) must be provided for Lyria.")

        self.client = genai.Client(api_key=self.api_key)
        self.model_id = settings.LYRIA_MODEL
        self.clip_model_id = settings.LYRIA_CLIP_MODEL

    async def generate_music(
        self, prompt: str, duration_seconds: int = 30, genre: Optional[str] = None, mood: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a track and save it under OUTPUT_DIR/music. Returns the real file, never a sample."""
        model = self.clip_model_id if duration_seconds <= 30 else self.model_id
        text = f"{prompt}\nGenre: {genre or 'any'}. Mood: {mood or 'any'}."
        if model == self.model_id:
            text += f" Length: about {duration_seconds} seconds."
        try:
            logger.info("Generating music with %s: %s...", model, prompt[:50])
            interaction = await asyncio.to_thread(self.client.interactions.create, model=model, input=text)
            audio = getattr(interaction, "output_audio", None)
            if not audio or not getattr(audio, "data", None):
                return {
                    "status": "error",
                    "error_type": "no_audio",
                    "error": f"{model} returned no audio",
                    "model": model,
                }

            out_dir = Path(settings.OUTPUT_DIR) / "music"
            out_dir.mkdir(parents=True, exist_ok=True)
            job_id = f"lyria_{uuid.uuid4().hex[:12]}"
            out_path = out_dir / f"{job_id}.mp3"
            out_path.write_bytes(base64.b64decode(audio.data))
            return {
                "status": "success",
                "job_id": job_id,
                "file_path": str(out_path),
                "lyrics": getattr(interaction, "output_text", None),
                "duration": 30 if model == self.clip_model_id else duration_seconds,
                "model": model,
            }
        except Exception as e:
            logger.error("Lyria generation failed: %s", e)
            return {"status": "error", "error": str(e), "model": model}


_provider: Optional[LyriaProvider] = None


def get_lyria_provider() -> LyriaProvider:
    """Lazily create the provider (the old module-level instance raised at import without a key)."""
    global _provider
    if _provider is None:
        _provider = LyriaProvider()
    return _provider
